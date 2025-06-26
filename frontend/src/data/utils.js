function getCurrentDateString(days_offset=0) {
    const date = new Date();
    date.setDate(date.getDate() - days_offset);
    const year = date.getFullYear();
    const month = String(date.getMonth() + 1).padStart(2, '0'); // Ensure two digits
    const day = String(date.getDate()).padStart(2, '0'); // Ensure two digits

    return `${year}-${month}-${day}`;
}

async function getFirebaseEndpoint({data_ref, order_by, limit_to_last, limit_to_first}) {
    const dbUrl = import.meta.env.VITE_FIREBASE_REALTIME_DB_URL;
    let endpoint = `${dbUrl}/${data_ref}.json`;
    let query_params = "";
    if (!order_by && (limit_to_last || limit_to_first)) {
        throw new Error("Cannot use limit_to_last, limit_to_first, or select without order_by");
    }
    if (order_by) {
        query_params += `?orderBy=${order_by}`;
    }
    if (limit_to_last) {
        query_params += `&limitToLast=${limit_to_last}`;
    } else if (limit_to_first) {
        query_params += `&limitToFirst=${limit_to_first}`;
    }
    endpoint += query_params;
    console.log(`FIREBASE REQUEST: ${endpoint}`);

    try {
        const response = await fetch(endpoint);
        if (!response.ok) {
            throw new Error(`HTTP error! Status: ${response.status}`);
        }
        return await response.text();
    } catch (error) {
        console.error("Error fetching data:", error);
        return null;
    }
}


function getDatesRange(start_days_offset, days_offset) {
    /** Get a range of dates starting *most recent* from start_days_offset days ago, with a total of days_offset days **/
    const dates = [];
    for (let i = start_days_offset; i < days_offset+start_days_offset; i++) {
        const dateString = getCurrentDateString(i);
        dates.push(dateString);
    }
    return dates;
}


export { getCurrentDateString, getDatesRange, getFirebaseEndpoint };