/** @odoo-module **/

import publicWidget from "@web/legacy/js/public/public_widget";

publicWidget.registry.SchoolFeatures = publicWidget.Widget.extend({

    selector: ".school-feature",

    start() {

        const element = this.el;

        const delay = parseInt(
            element.dataset.animationDelay || 0,
            10
        );

        // Initial state
        element.style.opacity = "0";
        element.style.transform = "translateY(40px)";

        setTimeout(() => {

            element.animate(
                [
                    {
                        opacity: 0,
                        transform: "translateY(40px)"
                    },
                    {
                        opacity: 1,
                        transform: "translateY(0)"
                    }
                ],
                {
                    duration: 700,
                    delay: 0,
                    easing: "ease-out",
                    fill: "forwards"
                }
            );

        }, delay);

        return this._super(...arguments);
    },

});