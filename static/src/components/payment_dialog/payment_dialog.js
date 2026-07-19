/** @odoo-module **/

import { Component, useState,onWillStart } from "@odoo/owl";
import { Dialog } from "@web/core/dialog/dialog";
import {useService} from "@web/core/utils/hooks"

export class PaymentDialog extends Component {
    static template = "school_base.PaymentDialog";
    static components = { Dialog };

    static props = {
        close: Function,
        fee: Object,
        studentName: String,
    };

    setup() {
        this.state = useState({
            paymentMethod: "",
            amountToPay: this.props.fee.due_amount,
            paymentMethods: []
        });
        this.orm = useService("orm")

        onWillStart(async ()=>{
            await this.getPaymentMathods();
            
        })
    }

    

    getPaymentMathods = async () =>{
        let domain = [['code', '!=', 'manual'], ['name', '!=', 'Manual']]
        const data = await this.orm.searchRead('school.payment.method',domain, ['name','code'])
        this.state.paymentMethods = data
    }

    get monthName() {
        return this.props.fee.batch_id[1];
    }

    get totalAmount() {
        return this.props.fee.paid_amount + this.props.fee.due_amount;
    }

    get dueAmount() {
        return this.props.fee.due_amount;
    }

    onMethodChange(ev) {
        this.state.paymentMethod = ev.target.value;
    }

    onAmountChange(ev) {
        this.state.amountToPay = parseFloat(ev.target.value) || 0;
    }

    payNow() {
        if (!this.state.paymentMethod) {
            alert("Please select a payment method");
            return;
        }
        if (this.state.amountToPay <= 0 || this.state.amountToPay > this.dueAmount) {
            alert("Please enter a valid amount");
            return;
        }

        console.log("Paying", {
            fee_line_id: this.props.fee.id,
            amount: this.state.amountToPay,
            method: this.state.paymentMethod,
        });

        // TODO: call this.orm.call(...) here to create the payment record

        this.props.close();
    }
}