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
            paymentMethod: null,
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

        const methodCode = ev.target.value;

        this.state.paymentMethod =
            this.state.paymentMethods.find(
                method => method.code === methodCode
            ) || null;
    }

    onAmountChange(ev) {
        this.state.amountToPay = parseFloat(ev.target.value) || 0;
    }

    async payNow() {

        if (!this.state.paymentMethod) {
            alert("Please select a payment method.");
            return;
        }

        if (
            this.state.amountToPay <= 0 ||
            this.state.amountToPay > this.dueAmount
        ) {
            alert("Please enter a valid amount.");
            return;
        }

        const result = await this.orm.call(
            "school.fee.payment",
            "student_pay_fee",
            [
                {
                    fee_line_id: this.props.fee.id,
                    payment_method_id: this.state.paymentMethod.id,
                    amount: this.state.amountToPay,
                }
            ]
        );

        console.log(result);

        if (
            result.success &&
            result.redirect_url
        ) {
            window.location.href = result.redirect_url;
            return;
        }

        this.props.close();
    }
}