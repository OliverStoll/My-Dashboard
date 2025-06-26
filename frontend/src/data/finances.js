import { getCurrentDateString, getFirebaseEndpoint} from "./utils.js";


async function getBudgetBakersBalance(account = "Alltag") {
    const todayDate = getCurrentDateString();
    const data_ref = `DATA/Finanzen/BudgetBakers/balances/${account}/${todayDate}/balance`;
    const balance_str = await getFirebaseEndpoint({data_ref: data_ref});
    return parseFloat(balance_str);
}


export { getBudgetBakersBalance };