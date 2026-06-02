import {registry} from "@web/core/registry"
import { Component, useState, onWillStart } from "@odoo/owl"
import {useService} from "@web/core/utils/hooks"
import {KpiCard} from "../components/kpi_card/kpi_card"
import {user} from "@web/core/user"
export class SchoolStudentDashboard extends Component{
    setup(){
        this.userId = user.userId
        this.state = useState({
            studentInfo:{
                student_id: null,
                name: "",
                email: '',
                code: '',
                active:null,
                admission_date:'',
                image: '',
            },
            accademic_year: {},
        })
        

        this.orm = useService("orm");
        onWillStart(async ()=>{
            await this.getAccademicYear();
            await this.getStudentInfo();
        })


        
    }
    getAccademicYear = async () => {
        const today = new Date().toISOString().split('T')[0]; // format: YYYY-MM-DD
        const domain = [
            ['date_start', '<=', today],
            ['date_end', '>=', today]
        ];

        const data = await this.orm.searchRead(
            "school.academic.year",
            domain,
            ['name', 'date_start', 'date_end']
        );

        // If you only expect one match:
        this.state.accademic_year = data.length ? data[0] : {};
    };

    getStudentInfo = async () =>{
        let domain = [['user_id', '=', this.userId]]
        const data = await this.orm.searchRead("school.student", domain, ['name', 'code','gender', 'admission_date', 'active', 'email', 'image'])
        
        this.state.studentInfo.name = data[0].name
        this.state.studentInfo.student_id = data[0].id
        this.state.studentInfo.email = data[0].email
        this.state.studentInfo.image = data[0].image
        this.state.studentInfo.active = data[0].active
        this.state.studentInfo.code = data[0].code

    }

    getStudentAttendances = async () =>{
        let domain = [['student_id', '=', this.state.studentInfo.student_id], ['']]
        const data = await this.orm.searchRead("school.student.attendance.line")
    }
}

SchoolStudentDashboard.template = "school_base.SchoolStudentDashboard"
SchoolStudentDashboard.components = {
    KpiCard
}
registry.category("actions").add("school_base.student_dashboard", SchoolStudentDashboard)