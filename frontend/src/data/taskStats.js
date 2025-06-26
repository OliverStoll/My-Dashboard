import {getCurrentDateString, getFirebaseEndpoint} from "./utils";


function calculateAverageCount(focusTimes, days_range, day_start=10, day_end=22) {
    const lastIncludedDate = getCurrentDateString(days_range);
    const focusDates = {}
    for (const date in focusTimes) {
        if (date >= lastIncludedDate) {
            focusDates[date] = focusTimes[date];
        }
    }

    let dailyAvgs  = []
    for (const focusDay of Object.values(focusDates)) {
        let focusHours = [];
        for (const [time, focusHour] of Object.entries(focusDay)) {
            if (Number(time) < day_start || Number(time) > day_end) {
                continue;
            }
            let focusMinutes = [];
            for (const focusMinute of Object.values(focusHour)) {
                focusMinutes.push(focusMinute);
            }
            const focusHourAvg = focusMinutes.reduce((a, b) => a + b, 0) / focusMinutes.length;
            focusHours.push(focusHourAvg);
        }
        if (focusHours.length === 0) {
            continue
        }
        const dailyAvg = focusHours.reduce((a, b) => a + b, 0) / focusHours.length;
        dailyAvgs.push(Number(dailyAvg.toFixed(2)));
    }
    console.log("TASKS - Daily Averages:", dailyAvgs);
    const dailyAvgSum = dailyAvgs.reduce((a, b) => a + b, 0)
    const totalAvg = dailyAvgSum / dailyAvgs.length;
    return totalAvg;
}



async function getTaskStats(days_range = 7) {
    const dataRef = "DATA/Tasks/TickTick/Aktive-Aufgaben-Stats";
    const data = await getFirebaseEndpoint({data_ref: dataRef, order_by: "%22$key%22", limit_to_last: days_range});
    const focusTimes = JSON.parse(data);
    return calculateAverageCount(focusTimes, days_range);
}

export { getTaskStats };