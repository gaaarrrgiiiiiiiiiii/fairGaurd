import React from 'react';
import {
  LineChart, Line, XAxis, YAxis, CartesianGrid,
  Tooltip, Legend, ResponsiveContainer, ReferenceLine,
} from 'recharts';
import type { ChartDataPoint } from '../types';

interface Props {
  data: ChartDataPoint[];
}

const BiasMetricsChart: React.FC<Props> = ({ data }) => (
  <div className="card-wrapper" style={{ height: '350px' }}>
    <h2 className="card-title">Fairness Thresholds Over Time</h2>
    <ResponsiveContainer width="100%" height="100%">
      <LineChart data={data}>
        <CartesianGrid strokeDasharray="3 3" stroke="#2a364a" />
        <XAxis dataKey="timestamp" stroke="#6b7280" />
        <YAxis stroke="#6b7280" domain={[0, 0.4]} />
        <Tooltip
          contentStyle={{ backgroundColor: '#151c28', borderColor: '#2a364a', color: 'white' }}
          itemStyle={{ color: 'white' }}
        />
        <Legend />
        <ReferenceLine y={0.15} label="ICD Threshold" stroke="#ef4444" strokeDasharray="3 3" />
        <Line
          type="monotone"
          dataKey="icd_score"
          name="Individual Disparity"
          stroke="var(--accent-yellow)"
          strokeWidth={2}
          dot={false}
          isAnimationActive={false}
        />
        <Line
          type="monotone"
          dataKey="dpd_score"
          name="Demographic Parity"
          stroke="var(--accent-green)"
          strokeWidth={2}
          dot={false}
          isAnimationActive={false}
        />
      </LineChart>
    </ResponsiveContainer>
  </div>
);

export default BiasMetricsChart;
