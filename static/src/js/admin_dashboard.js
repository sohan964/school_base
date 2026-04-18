import {registry} from "@web/core/registry"
import {Component, useState, onWillStart} from "@odoo/owl"
import {useService} from "@web/core/utils/hooks"
export class SchoolAdminDashboard extends Component{
    setup(){
        this.state = useState({
            students:{value:0},
            teachers:{value:0},
            classes:{value:0},
            departments:{value:0}
        })

        this.orm = useService("orm")

        onWillStart(async ()=>{
            await this.getAllStudent()
            await this.getAllTeacher()
            await this.getAllClass()
            
        })
    }

    getAllStudent = async() =>{
        let domain = []
        const data = await this.orm.searchCount("school.student", domain)
        console.log(data)
        this.state.students.value = data
    }

    getAllTeacher = async() =>{
        let domain = []
        const data = await this.orm.searchCount("school.teacher", domain)
        this.state.teachers.value = data
    }

    getAllClass = async()=>{
        let domain = []
        const data = await this.orm.searchCount("school.class", domain)
        this.state.classes.value = data
    }

    getAllDepartment = async()=>{
        let domain = []
        const data = await this.orm.searchCount("school.department", domain)
        this.state.departments.value = data
    }

    
}

SchoolAdminDashboard.template = "school_base.SchoolAdminDashboard"
// SchoolAdminDashboard.components = {

// }

registry.category("actions").add("school_base.admin_dashboard", SchoolAdminDashboard)