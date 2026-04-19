import { registry } from "@web/core/registry"
import { Component, useState, onWillStart } from "@odoo/owl"
import { useService } from "@web/core/utils/hooks"
import { KpiCard } from "../components/kpi_card/kpi_card"
import { ChartRenderer } from "../components/chart_renderer/chart_renderer"
export class SchoolAdminDashboard extends Component {
    setup() {
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

            }
        })

        this.orm = useService("orm")

        onWillStart(async () => {
            await this.getAllStudent()
            await this.getAllTeacher()
            await this.getAllClass()
            await this.getAllDepartment()
            await this.getAccademicYear()
            await this.getTodayAcademicSchedule()
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
        this.state.accademic_year = data[0];
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

    // getTodayAttendance = async ()=>{
    //     const today = new Date().toISOString().split('T')[0];
    //     const domain = []
    //     const totalAttendance = await this.orm.searchCount('')
    // }




}

SchoolAdminDashboard.template = "school_base.SchoolAdminDashboard"
SchoolAdminDashboard.components = {
    KpiCard, ChartRenderer
}

registry.category("actions").add("school_base.admin_dashboard", SchoolAdminDashboard)