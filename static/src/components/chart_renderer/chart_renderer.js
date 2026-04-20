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
        new Chart(this.chartRef.el, {
            type: this.props.type || 'bar',
            data: this.props.data,
            options: this.props.options || {}
        })
    }
}

ChartRenderer.template = "school_base.ChartRenderer"