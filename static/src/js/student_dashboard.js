import {registry} from "@web/core/registry"
import { Component, useState, onWillStart } from "@odoo/owl"
import {useService} from "@web/core/utils/hooks"
import {KpiCard} from "../components/kpi_card/kpi_card"
import {ChartRenderer} from "../components/chart_renderer/chart_renderer"
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
            academic_year: {},
            attendanceStats:{
                total:0,
                present:0,
                absent:0,
                late:0,
                attendancePercentage:0,
            },
            academicStats:{
                class: {},
                department:{},
                section: {},

            },
            subjectStats:{
                subjects:[],
                totalSubject: 0,
            },
            examStats:{
                exams:[],
                totalExam: 0,
            },
            resultStats:{
                subjectResults:[],
                averagePercentage: 0,
            },
            routineStats:{
                today:"",
                routine: []

            }
        })
        

        this.orm = useService("orm");
        onWillStart(async ()=>{
            await this.getAccademicYear();
            await this.getStudentInfo();
            await this.getStudentAttendances();
            await this.getAcademicStats();
            await this.getStudentSubjects();
            await this.getUpcomingExams();
            await this.getExamResults();
            await this.getTodaysRoutine();
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
        this.state.academic_year = data.length ? data[0] : {};
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
        let domain = [['student_id', '=', this.state.studentInfo.student_id], ['attendance_id.year_id', '=', this.state.academic_year.id]]
        const data = await this.orm.searchRead("school.student.attendance.line", domain, ['status'])
        
        const total = data.length;
        let present = 0;
        let late = 0;
        let absent = 0;

        data.forEach(item => {
            if (item.status === "present") present++;
            else if (item.status === "late") late++;
            else if (item.status === "absent") absent++;
        });
        
        const attendancePercentage = total > 0 ? (((present+late)/total)*100).toFixed(2) : 0;

        this.state.attendanceStats = {
            total,
            present,
            absent,
            late,
            attendancePercentage,
        };
    }

    getAcademicStats = async () =>{
        let domain = [['student_id', '=', this.state.studentInfo.student_id], ['year_id', '=', this.state.academic_year.id]]
        const data = await this.orm.searchRead("school.student.enrollment", domain, ['class_id', 'department_id', 'section_id']);
        this.state.academicStats.class = data[0].class_id
        this.state.academicStats.department = data[0].department_id
        this.state.academicStats.section = data[0].section_id
        
    }

    getStudentSubjects = async () =>{
        let domain = [['department_ids', 'in', this.state.academicStats.department[0]],['class_ids', 'in', this.state.academicStats.class[0]]]
        const data = await this.orm.searchRead('school.class.subject', domain, ['name', 'code'])
        const total = data.length
        this.state.subjectStats.totalSubject = total;
        this.state.subjectStats.subjects = data;
        console.log(this.state.subjectStats);

    }

    getUpcomingExams = async () =>{
        const today = new Date();
        const startDate = today.toISOString().split('T')[0];
        const endDateObj = new Date(
            today.getFullYear(),
            today.getMonth() + 1,
            10
        );
        const endDate = endDateObj.toISOString().split('T')[0];
        
        const domain = [
            ['department_id', '=', this.state.academicStats.department[0]],
            ['class_id', '=', this.state.academicStats.class[0]],
            ['exam_date', '>=', startDate],
            ['exam_date', '<=', endDate]
        ]

        const data = await this.orm.searchRead("school.exam.line", domain,
            [
                'display_name',
                'subject_id',
                'exam_date',
                'full_marks',
                'exam_time_slot_id'
            ]
        )
        this.state.examStats.totalExam = data.length;
        this.state.examStats.exams = data;
        
        // console.log(this.state.examStats.exams)

    }

    getExamResults = async () =>{
        let domain = [
            ['student_id', '=', this.state.studentInfo.student_id],
            ['result_id.year_id', '=', this.state.academic_year.id ]
        ]

        const data = await this.orm.searchRead("school.exam.result.line", domain, ['subject_id','marks_obtained', 'full_marks'])
        console.log(data);
        let totalPercentage = 0;

        const subjectResults = data.map(line =>{
            const percentage = line.full_marks > 0 ? (line.marks_obtained / line.full_marks) * 100 : 0;
            totalPercentage += percentage;
            return {
                subject_id: line.subject_id[0],
                subject_name: line.subject_id[1],
                obtained: line.marks_obtained,
                full_marks: line.full_marks,
                percentage: percentage.toFixed(2)
            };
        });
        const averagePercentage = subjectResults.length ? (totalPercentage / subjectResults.length).toFixed(2) : 0;

        this.state.resultStats.subjectResults = subjectResults;
        this.state.resultStats.averagePercentage = averagePercentage;

    }

    getTodaysRoutine = async () =>{
        const days = ['Sunday', 'Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday'];
        const todayName = days[new Date().getDay()];

        // Format today's date (YYYY-MM-DD)
        // const today = new Date().toISOString().split('T')[0];
        this.state.routineStats.today = todayName

        let domain = [
            ['department_id','=', this.state.academicStats.department[0]],
            ['class_id', '=', this.state.academicStats.class[0]],
            ['section_id', '=', this.state.academicStats.section[0]],
            ['day_id.name', '=', todayName],
            ['year_id', '=', this.state.academic_year.id]
        ]
        
        const data = await this.orm.searchRead("school.teacher.assignment",domain, ['slot_id', 'subject_id', 'teacher_id']);
        this.state.routineStats.routine = data;
    }
}

SchoolStudentDashboard.template = "school_base.SchoolStudentDashboard"
SchoolStudentDashboard.components = {
    KpiCard, ChartRenderer
}
registry.category("actions").add("school_base.student_dashboard", SchoolStudentDashboard)