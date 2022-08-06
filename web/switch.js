import { tiers } from "./data.js"

const tierlist = tiers.map(tier => tier.name.toLowerCase()).reverse()
const switchBtn = document.querySelector("#switch")

switchBtn.addEventListener("change", () => tierlist.forEach(tier => changeTable(tier)))

function changeTable(tier_table) {
    document.querySelectorAll(`#${tier_table}-table .player-row *`).forEach((element, i) => {
        const tier = element.getAttribute("tier")

        if (!tier) return;
        if (tierlist.indexOf(tier) <= tierlist.indexOf(tier_table)) {
            tierlist.indexOf(tier) < tierlist.indexOf(tier_table) &&
                (switchBtn.checked
                    ? (element.style.fontWeight = 800)
                    : (element.style.fontWeight = ""))
        } else {
            switchBtn.checked
                ? (element.style.backgroundColor = "grey")
                : (element.style.backgroundColor = "")
        }
    });
}
