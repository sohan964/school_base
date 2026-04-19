import { Component, onWillStart, useRef, onMounted } from "@odoo/owl"
import { loadJS } from "@web/core/assets"

export class ChartRenderer extends Component {
    setup() {
        this.chartRef = useRef("chart")
        onWillStart(async () => {
            await loadJS("https://cdnjs.cloudflare.com/ajax/libs/Chart.js/4.5.0/chart.umd.min.js")
        })
        onMounted(() => this.renderChart())
    }
    renderChart() {

        new Chart(
            this.chartRef.el,
            {
                type: "doughnut",
                data: {
                    labels: [
                        "Present", "Absent", "Late"
                    ],
                    datasets: [
                        {
                            label: "Attendance Rate",
                            data: [300, 50, 100],
                            backgroundColor: [
                                'rgb(40, 167, 69)',
                                'rgb(212, 76, 89)',
                                'rgb(233, 157, 0)'
                            ],
                            hoverOffset: 4
                        }
                    ]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    plugins: {
                        legend: {
                            position: 'bottom',
                        },
                        title: {
                            display: true,
                            text: "Attendance chart",
                            position: 'bottom',
                        }
                    }
                }
            }
        )
    }
}

ChartRenderer.template = "school_base.ChartRenderer"