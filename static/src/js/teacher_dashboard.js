import { registry } from "@web/core/registry"
import { Component, useState, onWillStart } from "@odoo/owl"
import { useService } from "@web/core/utils/hooks"
import {user} from  "@web/core/user";
import { ChartRenderer } from "../components/chart_renderer/chart_renderer";
import { KpiCard } from "../components/kpi_card/kpi_card";
export class SchoolTeacherDashboard extends Component{
    setup(){
        this.userId = user.userId
        this.state = useState({
            teacherinfo: {
                teacher_id: null,
                name: "",
                department: "",
                email:'',
                join_date:'',
                designation:'',
                image:''

            },
            teacherroutine: []
        })

        this.orm = useService("orm");
       
        onWillStart(async()=>{
            await this.getTeacherInfo()
            await this.getTeacherRoutine()
        })
    }

    getTeacherInfo = async () =>{
        
        let domain = [['user_id', '=', this.userId]]
        const data = await this.orm.searchRead("school.teacher", domain, ['name', 'department_id', 'email', 'joining_date','designation','image'])
        // console.log(data)
        this.state.teacherinfo.name = data[0].name
        this.state.teacherinfo.department = data[0].department_id[1]
        this.state.teacherinfo.email = data[0].email
        this.state.teacherinfo.join_date = data[0].joining_date
        this.state.teacherinfo.designation = data[0].designation
        this.state.teacherinfo.image = data[0].image
        this.state.teacherinfo.teacher_id = data[0].id
        console.log(this.state.teacherinfo)
    }

    getTeacherRoutine = async ()=>{
        const days = ['Sunday', 'Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday'];
        const todayName = days[new Date().getDay()];
        let domain = [['teacher_id', '=', this.state.teacherinfo.teacher_id], ['day_id.name','=', todayName]]
        const data = await this.orm.searchRead("school.teacher.assignment", domain, ['display_name'])
        this.state.teacherroutine = data
        console.log(this.teacherroutine)
    }
}

SchoolTeacherDashboard.template = "school_base.SchoolTeacherDashboard"
SchoolTeacherDashboard.components = {
    ChartRenderer, KpiCard
}
registry.category('actions').add("school_base.teacher_dashboard", SchoolTeacherDashboard)