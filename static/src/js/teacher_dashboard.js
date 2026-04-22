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
            teacherroutine: [],
            schedules:{
                total:0,
                taken:0,
                pending:0
            }
        })

        this.orm = useService("orm");
       
        onWillStart(async()=>{
            await this.getTeacherInfo()
            await this.getTeacherRoutine()
            await this.getTakenClasses()
            await this.getClassStudentCounts()
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
        const data = await this.orm.searchRead("school.teacher.assignment", domain, ['display_name', 'class_id', 'section_id'])
        console.log(data)

        this.state.teacherroutine = data
        

        this.state.schedules.total = data.length
         console.log(this.state.teacherroutine)
    }

    getTakenClasses = async() =>{
        const today = new Date().toISOString().split('T')[0];
        let domain = [['teacher_id', '=', this.state.teacherinfo.teacher_id], ['date', '=', today]]
        const data = await this.orm.searchCount('school.student.attendance', domain)
        this.state.schedules.taken = data
        this.state.schedules.pending = this.state.schedules.total - data
    }

    getClassStudentCounts = async()=>{
        const routine = this.state.teacherroutine
        console.log("routine",routine)
        // const orDomain = routine.map(pair => [
        //     '&',
        //     ['class_id', '=', pair.class_id[0]],
        //     ['section_id', '=', pair.section_id[0]]
        // ])
        let classDataCount = []
        for(let route of routine){
            console.log("this is ",route.class_id[0])
            let data = this.orm.searchCount("school.student.enrollment", [['class_id', '=', route.class_id[0]], ['section_id', '=', route.section_id[0]]])
            console.log("data",data)
        }
        
        // let finalDomain = []
        // if (orDomain.length === 1) {
        //     finalDomain = orDomain[0]
        // } else {
        //     finalDomain = ['|', ...orDomain.flat()]
        // }
        // console.log(finalDomain)

        // console.log(this.orm)
        // const data = await this.orm.searchRead(
        //     "school.student.enrollment",
        //     finalDomain,
        //     ['class_id', 'section_id', 'student_id']
        // )
        // const data = await this.orm.webReadGroup(
        //     "school.student.enrollment",
        //     finalDomain
        // )
        // console.log(data)

        // const result = data.map(item => ({
        //     class_id: item.class_id[0],
        //     class_name: item.class_id[1],
        //     section_id: item.section_id[0],
        //     section_name: item.section_id[1],
        //     total: item.__count
        // }))
        // console.log(result)
    }
}

SchoolTeacherDashboard.template = "school_base.SchoolTeacherDashboard"
SchoolTeacherDashboard.components = {
    ChartRenderer, KpiCard
}
registry.category('actions').add("school_base.teacher_dashboard", SchoolTeacherDashboard)