from odoo import models


class StudentResultReport(models.AbstractModel):
    _name = 'report.school_base.student_result_report'
    _description = 'Student Result Report'

    def _get_report_values(self, docids, data=None):

        student = self.env['school.student'].browse(docids).ensure_one()

        exam_id = data.get('exam_id')

        result_lines = self.env['school.exam.result.line'].search([
            ('student_id', '=', student.id),
            ('result_id.exam_id', '=', exam_id),
        ])

        grades = self.env['school.grade'].search([])

        subjects = []
        total_percentage = 0
        total_gpa = 0

        for line in result_lines:

            percentage = (
                (line.marks_obtained / line.full_marks) * 100
                if line.full_marks else 0
            )

            grade = grades.filtered(
                lambda g:
                g.min_mark <= percentage <= g.max_mark
            )[:1]

            subjects.append({
                'subject': line.subject_id.name,
                'obtained': line.marks_obtained,
                'full_marks': line.full_marks,
                'percentage': round(percentage, 2),
                'grade': grade.name if grade else '-',
                'gpa': grade.gpa if grade else 0,
            })

            total_percentage += percentage

            if grade:
                total_gpa += grade.gpa

        average_percentage = (
            total_percentage / len(subjects)
            if subjects else 0
        )

        average_gpa = (
            total_gpa / len(subjects)
            if subjects else 0
        )

        overall_grade = grades.filtered(
            lambda g:
            g.min_mark <= average_percentage <= g.max_mark
        )[:1]

        exam = self.env['school.exam'].browse(exam_id)

        # Get sample result record for header info
        sample_result = (
            result_lines[:1].result_id
            if result_lines else False
        )

        department = (
            sample_result.department_id
            if sample_result else False
        )

        class_obj = (
            sample_result.class_id
            if sample_result else False
        )

        section = (
            sample_result.section_id
            if sample_result else False
        )

        year = (
            sample_result.year_id
            if sample_result else False
        )

        enrollment = (
            result_lines[:1].enrollment_id
            if result_lines else False
        )

        roll_no = (
            enrollment.roll_no
            if enrollment else ''
        )

        return {
            'doc_ids': docids,
            'doc_model': 'school.student',
            'docs': student,

            'subjects': subjects,

            'exam': exam,
            'year': year,
            'department': department,
            'class_obj': class_obj,
            'section': section,
            'roll_no': roll_no,

            'average_percentage': round(
                average_percentage, 2
            ),

            'average_gpa': round(
                average_gpa, 2
            ),

            'overall_grade': (
                overall_grade.name
                if overall_grade else '-'
            ),
        }