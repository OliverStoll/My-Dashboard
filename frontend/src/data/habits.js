import { getCurrentDateString, getFirebaseEndpoint } from "./utils.js";


async function getHabitsMetadata(filterArchived=false) {
    const habitsMetadataRef = `DATA/Habits/Ticktick/Habits`;
    const habitsStr = await getFirebaseEndpoint({data_ref:habitsMetadataRef});
    const allHabitsDict = JSON.parse(habitsStr);
    if (filterArchived) {
        const activeHabitsDict = {};
        for (const [habitId, habitData] of Object.entries(allHabitsDict)) {
            if (habitData["status"] === 0) {
                activeHabitsDict[habitId] = habitData;
            }
        }
        return activeHabitsDict;
    }
    return allHabitsDict;
}


async function getHabitEntries(days_offset=14) {
    const entriesRef = `DATA/Habits/Ticktick/Eintraege`;
    const rawEntries = await getFirebaseEndpoint({
        data_ref: entriesRef,
        order_by: "%22$key%22",
        limit_to_last: days_offset
    });
    const firstIncludedDate = getCurrentDateString(days_offset - 1);
    const entriesDict = JSON.parse(rawEntries);
    let mappedEntries = {}
    for (const [entryDay, entryDayData] of Object.entries(entriesDict)) {
        if (entryDay < firstIncludedDate) {
            continue
        }
        for (const [habitId, entryData] of Object.entries(entryDayData)) {
            if (habitId in mappedEntries) {
                mappedEntries[habitId][entryDay] = entryData
            } else {
                mappedEntries[habitId] = {[entryDay]: entryData}
            }
        }
    }
    return mappedEntries
}


function getHabitGoalDaysPerWeek(habit_entry) {
    const repeatRule = habit_entry["repeatRule"];
    const byDay = repeatRule.split("BYDAY=")[1];
    const days = byDay.split(",");
    return days.length;
}


async function getHabitEntriesStat(days_offset=14) {
    const habitsMetadataPromise = getHabitsMetadata(true);
    const habitEntriesPromise = getHabitEntries(days_offset);
    const AllHabitsMetadata = await habitsMetadataPromise
    const allHabitEntries = await habitEntriesPromise;

    let totalAvg = [];
    for (const [habitId, habitEntries] of Object.entries(allHabitEntries)) {
        const habitMetadata = AllHabitsMetadata[habitId];
        if (!habitMetadata) {
            console.warn(`Habit metadata not found for ID: ${habitId}`);
            continue;
        }
        const goalDaysPerWeek = getHabitGoalDaysPerWeek(habitMetadata);
        const todayDate = getCurrentDateString(0);
        let todayIsCompleted = false;

        let completedEntries = 0
        for (const [date, habitEntry] of Object.entries(habitEntries)) {
            if (date === todayDate) {
                todayIsCompleted = true;
            }
            if (habitEntry.status === 2) {
                completedEntries += 1;
            }
        }
        let numDaysToConsider = days_offset;
        if (!todayIsCompleted) {
            numDaysToConsider -= 1;
        }

        const avgCompleted = completedEntries / numDaysToConsider
        const goalAvg = goalDaysPerWeek / 7
        const avgCompletedGoal = avgCompleted / goalAvg
        const roundedAvgCompletedGoal = Number(avgCompletedGoal.toFixed(3))
        totalAvg.push(roundedAvgCompletedGoal)
    }

    let totalAvgCompleted = totalAvg.reduce((a, b) => a + b, 0) / totalAvg.length;
    console.log("Habits - Total Habits Avg:", totalAvg);
    totalAvgCompleted = Math.round(totalAvgCompleted * 100) / 100;
    return totalAvgCompleted;
}



export { getHabitsMetadata, getHabitEntries, getHabitEntriesStat };