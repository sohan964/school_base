import { registry } from "@web/core/registry"
import { Component, useState, onWillStart } from "@odoo/owl"
import { useService } from "@web/core/utils/hooks"

export class SchoolTeacherDashboard extends Component{
    setup(){
        // this.user = useService("user");
        // console.log(this.user.context);

        this.state = useState({
            teacherinfo: {}

        })

        this.orm = useService("orm");
       
        onWillStart(async()=>{
            await this.getTeacherInfo()
        })
    }

    getTeacherInfo = async () =>{
        // super.setup();
        // this.currentUserId = this.props.activity.user_id[0];
        // console.log('Current User ID (from session):', this.currentUserId);

        //console.log(userId)
        let domain = []

    }
}

SchoolTeacherDashboard.template = "school_base.SchoolTeacherDashboard"

registry.category('actions').add("school_base.teacher_dashboard", SchoolTeacherDashboard)