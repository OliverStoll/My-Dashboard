import React from 'react';
import { CircularProgressbar, buildStyles } from 'react-circular-progressbar';
import 'react-circular-progressbar/dist/styles.css';
import * as d3 from 'd3';


const DynamicCircularProgressBar = ({percentage, text }) => {
    const clampedPercentage = Math.min(100, Math.max(5, percentage));
    const interpolateColor = d3.scaleLinear()
        .domain([0, 50, 100])
        .range(['red', 'yellow', 'green'])
        .clamp(true);
    const strokeColor = interpolateColor(percentage);
    text = text || `${percentage}`;

    return (
        <div >
            <CircularProgressbar
                value={clampedPercentage}
                text={`${text}`}
                strokeWidth={9.49}
                styles={buildStyles({
                    pathColor: strokeColor,
                    textColor: strokeColor,
                    trailColor: '#d6d6d6',
                    strokeLinecap: "butt",
                    shapeRendering: "geometricPrecision", // Enables anti-aliasing
                })}
            />
        </div>
    );
};

export default DynamicCircularProgressBar;

