import { registry } from "@web/core/registry"
import { Component, useState, onWillStart } from "@odoo/owl"
import { useService } from "@web/core/utils/hooks"
import {user} from  "@web/core/user";
export class SchoolTeacherDashboard extends Component{
    setup(){
        this.state = useState({
            teacherinfo: {
                name: "",
                department: "",
                email:'',
                join_date:'',
                designation:'',
                image:''

            }

        })

        this.orm = useService("orm");
       
        onWillStart(async()=>{
            await this.getTeacherInfo()
        })
    }

    getTeacherInfo = async () =>{
        const userId = user.userId
        let domain = [['user_id', '=', userId]]
        const data = await this.orm.searchRead("school.teacher", domain, ['name', 'department_id', 'email', 'joining_date','designation','image'])
        // console.log(data)
        this.state.teacherinfo.name = data[0].name
        this.state.teacherinfo.department = data[0].department_id[1]
        this.state.teacherinfo.email = data[0].email
        this.state.teacherinfo.join_date = data[0].joining_date
        this.state.teacherinfo.designation = data[0].designation
        this.state.teacherinfo.image = data[0].image
        // console.log(this.state.teacherinfo)



    }
}

SchoolTeacherDashboard.template = "school_base.SchoolTeacherDashboard"

registry.category('actions').add("school_base.teacher_dashboard", SchoolTeacherDashboard)