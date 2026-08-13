/** @odoo-module **/

import publicWidget from "@web/legacy/js/public/public_widget";

publicWidget.registry.SchoolStatsCounter = publicWidget.Widget.extend({

    selector: ".school-stat-number",

    start() {
        this.animateCounter();
        return this._super(...arguments);
    },

    animateCounter() {
        const counter = this.el;

        const target = parseInt(
            counter.dataset.target,
            10
        );

        if (!target) {
            return;
        }

        const duration = 1500;
        const startTime = performance.now();

        const update = (currentTime) => {

            const elapsed = currentTime - startTime;

            const progress = Math.min(
                elapsed / duration,
                1
            );

            const value = Math.floor(
                progress * target
            );

            counter.textContent =
                value.toLocaleString() + "+";

            if (progress < 1) {
                requestAnimationFrame(update);
            } else {
                counter.textContent =
                    target.toLocaleString() + "+";
            }
        };

        requestAnimationFrame(update);
    },

});