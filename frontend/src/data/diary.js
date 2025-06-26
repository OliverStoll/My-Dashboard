import { getCurrentDateString, getFirebaseEndpoint} from "./utils.js";


function getMoodValue(mood) {
    switch (mood) {
        case "Awesome":
            return 3;
        case "Happy":
            return 1;
        case "Neutral":
            return 0;
        case "Bad":
            return -1;
        case "Aweful":
            return -3;
        default:
            return 0;
    }
}

async function getMoods(max_days_old=14) {
    const data_ref = "DATA/Tagebuch/Diaro"
    const diary_entries = await getFirebaseEndpoint(
        {data_ref:data_ref, order_by: "%22$key%22", limit_to_last: max_days_old, select:"mood"} );
    const diary_entries_json = JSON.parse(diary_entries);
    const diary_dates = Object.keys(diary_entries_json).sort().reverse();
    const latest_date_str = getCurrentDateString(max_days_old);
    // filter out all entries smaller than the latest date (string comparison)
    const diary_dates_filtered = diary_dates.filter(date => date >= latest_date_str);
    const newest_entries = diary_dates_filtered.map(date => diary_entries_json[date]);
    const newest_moods = newest_entries.map(entry => entry["mood"]);
    const newest_mood_values = newest_moods.map(mood => getMoodValue(mood));
    console.log("Newest mood values", newest_mood_values);
    const average_mood = newest_mood_values.reduce((a, b) => a + b, 0) / newest_mood_values.length;
    console.log("Average mood:", average_mood);
    return average_mood;
}

export { getMoods };

