import './App.css';
import React from 'react';
import { use } from 'react';
import DynamicCircularProgressBar from './CircularProgressBar.jsx';
import {getBudgetBakersBalance} from "./data/finances.js";
import {getSanitasWeight} from "./data/weight.js";
import {getHabitEntriesStat} from "./data/habits.js";
import {getTaskStats} from "./data/taskStats.js";
import {getAvgDailyFocusTime} from "./data/focusTime.js";
import {max, sum} from "simple-statistics";


const balancePromise = getBudgetBakersBalance();
const weightPromise = getSanitasWeight();
const habitNames = ["Kardio", "Meditieren", "Tagebuch", "Training", ]
const habitStatsPromise = getHabitEntriesStat(14, habitNames);
const taskStatsPromise = getTaskStats(14);
const focusTimePromise = getAvgDailyFocusTime(14)


function calculatePercentageScore(value, min, max, minScore=5) {
    const rawScore = (value - min) / (max - min) * 100
    const clampedScore = Math.min(100, Math.max(minScore, rawScore))
    return clampedScore
}

function BudgetBalance() {
    const maxBalance = 250;
    const minBalance = 0
    const balance = use(balancePromise);  // Automatically suspends until resolved
    const output_str = `${Math.round(balance / 10) * 10} €`;
    const balance_percentage = calculatePercentageScore(balance, minBalance, maxBalance)
    return [output_str, balance_percentage];
}

function Weight() {
    const max_trend = 0.5;
    const min_trend = -0.5;
    const weight_trend = use(weightPromise);  // Automatically suspends until resolved
    const output_str = weight_trend > 0 ? `+${weight_trend} kg` : `${weight_trend} kg`;
    const weightScoreNegative = calculatePercentageScore(weight_trend, min_trend, max_trend)
    let weight_percentage = 100 - weightScoreNegative
    return [output_str, weight_percentage];
}

function FocusTime() {
    const minFocusTime = 0
    const maxFocusTime = 240
    const avgFocusTime = use(focusTimePromise)
    const avgFocusHours = avgFocusTime / 60
    const outputText = `${avgFocusHours.toFixed(1)} h`
    const focusScore = calculatePercentageScore(avgFocusTime, minFocusTime, maxFocusTime)
    return [outputText, focusScore]
}

function Moods() {
    const minMood = -1;
    const maxMood = 0.5;
    const averageMood = use(moodPromise);  // Automatically suspends until resolved
    const mood_percentage = (averageMood - minMood) / (maxMood - minMood) * 100;
    let mood_text = "";
    if (averageMood >= 0.6) {
        mood_text = "Sehr Gut";
    } else if (averageMood >= 0.3) {
        mood_text = "Gut";
    } else if (averageMood >= -0.3) {
        mood_text = "Neutral";
    } else if (averageMood >= -1) {
        mood_text = "Geht so";
    } else {
        mood_text = "Schlecht";
    }
    return [mood_text, mood_percentage];
}

function Habits() {
    const habitStats= use(habitStatsPromise) * 100
    const habitText = habitStats.toFixed(0) + "%";
    const minHabit = 0;
    const maxHabit = 90;
    let habitPercentage = (habitStats - minHabit) / (maxHabit - minHabit) * 100;
    habitPercentage = Math.min(100, Math.max(0, habitPercentage));
    return [habitText, habitPercentage];
}


function TaskStats() {
    const averageCount = use(taskStatsPromise);
    const maxCount = 7;
    const minCount = 1;
    let taskPercentage = (averageCount - minCount) / (maxCount - minCount) * 100;
    taskPercentage = 100 - taskPercentage;
    taskPercentage = Math.min(100, Math.max(0, taskPercentage));
    const task_text = `${averageCount.toFixed(0)}`;
    return [task_text, taskPercentage];
}



function AllCircularProgressBars() {
    //const [budgetText, budgetPercentage] = BudgetBalance();
    //const [weightText, weightPercentage] = Weight();
    const [habitText, habitPercentage] = Habits();
    const [taskText, taskPercentage] = TaskStats();
    const [focusText, focusPercentage] = FocusTime();
    const percentages = [habitPercentage, taskPercentage, focusPercentage];
    const sumPercentage =  percentages.reduce((acc, val) => acc + val, 0);
    const avgPercentage = sumPercentage / percentages.length;
    const opacityVal = (1 - (avgPercentage / 100)).toFixed(2);
    const backgroundOpacity = (0.15 * avgPercentage / 100).toFixed(2);

    return (
        <div className="results-wrapper">
            <div style={{'--final-opacity': backgroundOpacity}} className='background2 fade-in'></div>
            <div style={{'--final-opacity': opacityVal}} className="progress-bar-wrapper fade-in">
                <div className="progress-bar-container">
                    <h2>Habits</h2>
                    <DynamicCircularProgressBar percentage={habitPercentage} text={habitText}/>
                </div>
                <div className="progress-bar-container">
                    <h2>Fokus</h2>
                    <DynamicCircularProgressBar percentage={focusPercentage} text={focusText}/>
                </div>
                <div className="progress-bar-container">
                    <h2>To-Do's</h2>
                    <DynamicCircularProgressBar percentage={taskPercentage} text={taskText}/>
                </div>
            </div>
        </div>
    );
}


const App = () => {
    return (
        <div className="App-Wrapper">
            <div className="background"></div>
            <React.Suspense>
                <AllCircularProgressBars />
            </React.Suspense>
        </div>
    );
};

export default App;
