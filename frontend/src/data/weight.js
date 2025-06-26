import { getDatesRange, getCurrentDateString, getFirebaseEndpoint} from "./utils.js";
import * as ss from 'simple-statistics';



function calculateWeightedAverage(weight_entries, days_average, days_comparison, ignore_null=true) {
    let weighted_averages= [];
    for (let currentDayOffset = 0; currentDayOffset < days_comparison; currentDayOffset++) {
        const dates_strings = getDatesRange(currentDayOffset, days_average);
        let fitting_entries = [];
        for (const date_str of dates_strings) {
            if (weight_entries[date_str]) {
                fitting_entries.push(weight_entries[date_str]);
            }
        }
        if (fitting_entries.length === 0) {
            if (!ignore_null) {
                weighted_averages.push(null);
            }
            continue;
        }
        const average = fitting_entries.reduce((a, b) => a + b, 0) / fitting_entries.length;
        const avg_rounded = Number(average.toFixed(2));
        weighted_averages.push(avg_rounded);
    }
    return weighted_averages.reverse();
}


async function getSanitasWeight(days_average=3, days_comparison=21) {
    const data_ref = `DATA/Gewichtsdaten/Sanitas`;
    const total_days = days_average + days_comparison;
    const weight_str = await getFirebaseEndpoint({data_ref: data_ref, order_by: "%22$key%22", limit_to_last: total_days});
    const weight_dict = JSON.parse(weight_str);
    const cutoff_date_str = getCurrentDateString(total_days);
    let weight_entries = {};
    for (const [date, weight_entry] of Object.entries(weight_dict)) {
        const date_str = date.slice(0, 10);
        if (date_str >= cutoff_date_str) {
            // only a random entry for each day is kept (TODO: improve this)
            weight_entries[date_str] = weight_entry["weight"];
        }
    }
    const weighted_averages = calculateWeightedAverage(weight_entries, days_average, days_comparison);
    const weighted_avgs_paired = weighted_averages.map((y, x) => [x, y]);
    const { m: dailyChange } = ss.linearRegression(weighted_avgs_paired);
    const weekly_trend = Number((dailyChange * 7).toFixed(1));
    return weekly_trend;
}

export { getSanitasWeight };