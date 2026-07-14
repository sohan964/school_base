import { registry } from "@web/core/registry";
import { Component, useState, onWillStart } from "@odoo/owl"
import { useService } from "@web/core/utils/hooks"
import { KpiCard } from "../components/kpi_card/kpi_card"
import { ChartRenderer } from "../components/chart_renderer/chart_renderer"
import {user} from "@web/core/user"

export class SchoolAdminDashboard extends Component {
    setup() {

        
        console.log(user.userId)
        this.state = useState({
            students: { value: 0 },
            teachers: { value: 0 },
            classes: { value: 0 },
            departments: { value: 0 },
            accademic_year: {},
            todayacademicactivities: {
                classes_scheduled: 0,
                classes_completed: 0,
                classes_pendding: 0,
            },
            attendance_chart: {
                total: 0,
                present: 0,
                late: 0,
                absent: 0,
                attendance_parcent:0
            },
            adminRoutineStats: {
                dayId: null,
                slotId: null,

                days: [],
                slots: [],

                routines: [],
                total: 0,
            }


        })

        this.orm = useService("orm")

        onWillStart(async () => {
            await this.getAccademicYear()
            await this.getDays()
            await this.getTimeSlots()
            await this.getAdminRoutine()
            await this.getAllStudent()
            await this.getAllTeacher()
            await this.getAllClass()
            await this.getAllDepartment()
            
            await this.getTodayAcademicSchedule()
            await this.getTodayAttendanceStats()
        })
    }

    getAllStudent = async () => {
        let domain = []
        const data = await this.orm.searchCount("school.student", domain)

        this.state.students.value = data
    }

    getAllTeacher = async () => {
        let domain = []
        const data = await this.orm.searchCount("school.teacher", domain)
        this.state.teachers.value = data
    }

    getDays = async () =>{
        
        const days = await this.orm.searchRead(
            "school.weekly.day",
            [['active', '=', true]],
            ['name', 'code']
        );
        this.state.adminRoutineStats.days = days;

        const todayCode = [
            'sun',
            'mon',
            'tue',
            'wed',
            'thu',
            'fri',
            'sat'
        ][new Date().getDay()];

        const currentDay =
            days.find(d => d.code === todayCode);

        if (currentDay) {
            this.state.adminRoutineStats.dayId =
                currentDay.id;
        }
    }

    getTimeSlots = async() =>{
        const slots = await this.orm.searchRead(
            "school.time.slot",
            [['active', '=', true]],
            ['name', 'start_time', 'end_time']
        );

        this.state.adminRoutineStats.slots = slots;

        const now = new Date();

        const currentHour =
            now.getHours() +
            (now.getMinutes() / 60);

        const currentSlot =
            slots.find(slot =>
                currentHour >= slot.start_time &&
                currentHour < slot.end_time
            );

        if (currentSlot) {
            this.state.adminRoutineStats.slotId =
                currentSlot.id;
        }
    }

    //routine start
    onDayChange = async (ev) => {

        this.state.adminRoutineStats.dayId =
            parseInt(ev.target.value);

        await this.getAdminRoutine();
    }

    onSlotChange = async (ev) => {

        this.state.adminRoutineStats.slotId =
            parseInt(ev.target.value);

        await this.getAdminRoutine();
    }

    getAdminRoutine = async () => {

        let domain = [
            ['year_id', '=', this.state.accademic_year.id]
        ];
        console.log("year need",this.state.accademic_year)

        if (this.state.adminRoutineStats.dayId) {
            domain.push([
                'day_id',
                '=',
                this.state.adminRoutineStats.dayId
            ]);
        }

        if (this.state.adminRoutineStats.slotId) {
            domain.push([
                'slot_id',
                '=',
                this.state.adminRoutineStats.slotId
            ]);
        }

        const data = await this.orm.searchRead(
            "school.teacher.assignment",
            domain,
            [
                'teacher_id',
                'subject_id',
                'class_id',
                'section_id',
                'day_id',
                'slot_id'
            ]
        );

        this.state.adminRoutineStats.routines = data;
        this.state.adminRoutineStats.total = data.length;
    }

    getAllClass = async () => {
        let domain = []
        const data = await this.orm.searchCount("school.class", domain)
        this.state.classes.value = data
    }

    getAllDepartment = async () => {
        let domain = []
        const data = await this.orm.searchCount("school.department", domain)
        this.state.departments.value = data
    }

    getAccademicYear = async () => {
        const today = new Date().toISOString().split('T')[0]; // format: YYYY-MM-DD
        // console.log(today)
        const domain = [
            ['date_start', '<=', today],
            ['date_end', '>=', today]
        ];

        const data = await this.orm.searchRead(
            "school.academic.year",
            domain,
            ['name', 'date_start', 'date_end']
        );

        // console.log(data[0]);

        // If you only expect one match:
        
        this.state.accademic_year = data.length ? data[0] : {};
        console.log(this.state.accademic_year)
    };

    getTodayAcademicSchedule = async () => {
        const days = ['Sunday', 'Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday'];
        const todayName = days[new Date().getDay()];

        // Format today's date (YYYY-MM-DD)
        const today = new Date().toISOString().split('T')[0];
        const domain = [
            ['day_id.name', '=', todayName]
        ];
        const totalClass = await this.orm.searchCount(
            'school.teacher.assignment',
            domain
        );
        const completedClass = await this.orm.searchCount(
            'school.student.attendance',
            [['date', '=', today]]
        );
        this.state.todayacademicactivities.classes_scheduled = totalClass;
        this.state.todayacademicactivities.classes_completed = completedClass;
        this.state.todayacademicactivities.classes_pendding = totalClass - completedClass;
    };

    getTodayAttendanceStats = async () => {
        const today = new Date().toISOString().split('T')[0];

        const attendanceLines = await this.orm.searchRead(
            'school.student.attendance.line',
            [
                ['attendance_id.date', '=', today]
            ],
            ['student_id', 'status']
        );

        // Unique student tracking
        const studentMap = new Map();

        for (const line of attendanceLines) {
            if (!line.student_id) continue;

            const studentId = line.student_id[0];

            // If already counted → skip (avoid duplicates)
            if (!studentMap.has(studentId)) {
                studentMap.set(studentId, line.status);
            }
        }

        // Counters
        let present = 0;
        let absent = 0;
        let late = 0;

        for (const status of studentMap.values()) {
            if (status === 'present') present++;
            else if (status === 'absent') absent++;
            else if (status === 'late') late++;
        }
        let total = studentMap.size
        const attendancePercent = total > 0
        ? (((present + late) / total) * 100).toFixed(2)
        : 0;
        
        this.state.attendance_chart.total = total
        this.state.attendance_chart.present = present
        this.state.attendance_chart.absent = absent
        this.state.attendance_chart.late = late
        this.state.attendance_chart.attendance_parcent = attendancePercent
        console.log(this.state.attendance_chart)

    };

    

}

SchoolAdminDashboard.template = "school_base.SchoolAdminDashboard"
SchoolAdminDashboard.components = {
    KpiCard, ChartRenderer
}

registry.category("actions").add("school_base.admin_dashboard", SchoolAdminDashboard)