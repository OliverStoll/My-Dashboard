import {getCurrentDateString, getFirebaseEndpoint} from "./utils";


async function getFocusTimes(daysRange = 14) {
    const dataRef = "DATA/Arbeitszeiten/TickTick"
    const rawFocusData = await getFirebaseEndpoint({data_ref: dataRef, order_by: "%22$key%22", limit_to_last: daysRange})
    const focusData = JSON.parse(rawFocusData)
    const earliestIncludedDate = getCurrentDateString(daysRange-1)
    let filteredFocusData = Object.fromEntries(
        Object.entries(focusData).filter(([date, _]) => {
            return date >= earliestIncludedDate
        })
    )
    return filteredFocusData
}


function calculateDailyFocusTimes(focusData) {
    const dailyFocusTimes = []
    for (const focusTimes of Object.values(focusData)) {
        const focusTimesArray = Object.values(focusTimes)
        const dailyFocusTime = focusTimesArray.reduce((sum, obj) => sum + obj.totalDuration, 0)
        dailyFocusTimes.push(dailyFocusTime)
    }
    return dailyFocusTimes
}

async function getAvgDailyFocusTime(daysRange, workingDays=5) {
    const workingDaysPortion = workingDays / 7
    const focusData = await getFocusTimes(daysRange)
    const dailyFocusTimes = calculateDailyFocusTimes(focusData)
    const totalFocusTime = dailyFocusTimes.reduce((sum, value) => sum + value, 0)
    const avgDailyFocusTime = totalFocusTime / (daysRange * workingDaysPortion)
    return Math.round(avgDailyFocusTime)
}


export { getAvgDailyFocusTime }