import { registry } from "@web/core/registry"
import { Component, useState, onWillStart } from "@odoo/owl"
import { useService } from "@web/core/utils/hooks"
import { user } from "@web/core/user";
import { ChartRenderer } from "../components/chart_renderer/chart_renderer";
import { KpiCard } from "../components/kpi_card/kpi_card";
export class SchoolTeacherDashboard extends Component {
    setup() {
        this.userId = user.userId
        this.state = useState({
            teacherinfo: {
                teacher_id: null,
                name: "",
                department: "",
                email: '',
                join_date: '',
                designation: '',
                image: ''

            },
            teacherroutine: [],
            schedules: {
                total: 0,
                taken: 0,
                pending: 0
            },
            chartData:{},
            all_student:0,
            accademic_year:{},
            teacher_activities:{
                subjects:[]
            }
        })

        this.orm = useService("orm");

        onWillStart(async () => {
            await this.getAccademicYear()
            await this.getTeacherInfo()
            await this.getTeacherRoutine()
            await this.getTakenClasses()
            await this.getClassStudentCounts()
            this.prepareChartData()
            await this.getTeacherYearlyActivities()
        })
    }

    getTeacherInfo = async () => {

        let domain = [['user_id', '=', this.userId]]
        const data = await this.orm.searchRead("school.teacher", domain, ['name', 'department_id', 'email', 'joining_date', 'designation', 'image'])
        // console.log(data)
        this.state.teacherinfo.name = data[0].name
        this.state.teacherinfo.department = data[0].department_id[1]
        this.state.teacherinfo.email = data[0].email
        this.state.teacherinfo.join_date = data[0].joining_date
        this.state.teacherinfo.designation = data[0].designation
        this.state.teacherinfo.image = data[0].image
        this.state.teacherinfo.teacher_id = data[0].id
        // console.log(this.state.teacherinfo)
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
        this.state.accademic_year = data[0];
        console.log(this.state.accademic_year)
    };

    getTeacherRoutine = async () => {
        const days = ['Sunday', 'Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday'];
        const todayName = days[new Date().getDay()];
        let domain = [['teacher_id', '=', this.state.teacherinfo.teacher_id], ['day_id.name', '=', todayName], ['year_id','=', this.state.accademic_year.id]]
        const data = await this.orm.searchRead("school.teacher.assignment", domain, ['display_name', 'class_id', 'section_id', 'subject_id'])
        // console.log(data)

        this.state.teacherroutine = data

        this.state.schedules.total = data.length
        console.log(this.state.teacherroutine)
    }

    getTeacherYearlyActivities = async ()=>{
        let domain = [['teacher_id', '=', this.state.teacherinfo.teacher_id]]
        const data = await this.orm.searchRead("school.teacher.assignment", domain, ['subject_id', 'class_id'])

        const subjectMap = new Map()
        data.forEach(item =>{
            if(item.subject_id){
                const id = item.subject_id[0]
                const name = item.subject_id[1]
                subjectMap.set(id, {id, name});
            }
        })
        console.log("the map", subjectMap)
        this.state.teacher_activities.subjects = Array.from(subjectMap.values())
         console.log(this.state.teacher_activities.subjects)
        
    }

    getTakenClasses = async () => {
        const today = new Date().toISOString().split('T')[0];
        let domain = [['teacher_id', '=', this.state.teacherinfo.teacher_id], ['date', '=', today]]
        const data = await this.orm.searchCount('school.student.attendance', domain)
        this.state.schedules.taken = data
        this.state.schedules.pending = this.state.schedules.total - data
    }



    getClassStudentCounts = async () => {
        const routine = this.state.teacherroutine
        console.log("routine", routine)

        const finalDomain = [
            ['class_id', 'in', routine.map(r => r.class_id[0])],
            ['section_id', 'in', routine.map(r => r.section_id[0])]
        ]

        const data = await this.orm.searchRead(
            "school.student.enrollment",
            finalDomain,
            ['class_id', 'section_id', 'student_id']
        )

        const enrollmentMap = {}

        data.forEach(item => {
            enrollmentMap[item.id] = {
                class_id: item.class_id[0],
                class_name: item.class_id[1],
                section_id: item.section_id[0],
                section_name: item.section_id[1]
            }
        })

        this.state.all_student = data.length

        const map = {}

        data.forEach(item => {

            const key = `${item.class_id[0]}_${item.section_id[0]}`

            if (!map[key]) {
                map[key] = {
                    class_id: item.class_id[0],
                    class_name: item.class_id[1],
                    section_id: item.section_id[0],
                    section_name: item.section_id[1],
                    student_count: 0,
                    present: 0,
                    absent: 0
                }
            }

            map[key].student_count++
        })


        const today = new Date().toISOString().split('T')[0]

        const attendanceLines = await this.orm.searchRead(
            "school.student.attendance.line",
            [
                ['attendance_id.date', '=', today],
                ['attendance_id.teacher_id', '=', this.state.teacherinfo.teacher_id],
            ],
            ['status', 'enrollment_id']
        )
        console.log(attendanceLines)
        attendanceLines.forEach(line => {
            const enrollment = enrollmentMap[line.enrollment_id[0]]

            const key = `${enrollment.class_id}_${enrollment.section_id}`
            if (!map[key]) return
            if (line.status === 'present' || line.status === 'late') {
                map[key].present++
            } else {
                map[key].absent++
            }
        })
        const finalResult = Object.values(map)
        console.log(finalResult)
        this.state.classStudentStats = finalResult
    }

    prepareChartData = () => {

        const stats = this.state.classStudentStats || []

        const labels = stats.map(
            s => `${s.class_name} - ${s.section_name}`
        )

        const total = stats.map(s => s.student_count)
        const present = stats.map(s => s.present)
        const absent = stats.map(s => s.absent)

        this.state.chartData = {
            labels: labels,
            datasets: [
                {
                    label: 'Total Students',
                    data: total,
                    backgroundColor: '#0d6efd',
                    borderRadius: 6,
                    barThickness: 18
                },
                {
                    label: 'Present',
                    data: present,
                    backgroundColor: '#28a745',
                    borderRadius: 6,
                    barThickness: 18
                },
                {
                    label: 'Absent',
                    data: absent,
                    backgroundColor: '#dc3545',
                    borderRadius: 6,
                    barThickness: 18
                }
            ]
        }
    }


}

SchoolTeacherDashboard.template = "school_base.SchoolTeacherDashboard"
SchoolTeacherDashboard.components = {
    ChartRenderer, KpiCard
}
registry.category('actions').add("school_base.teacher_dashboard", SchoolTeacherDashboard)