import React from 'react';
import {
  LineChart, Line,
  Tooltip, Legend, ResponsiveContainer,
} from 'recharts';
import type { ChartDataPoint } from '../types';

interface Props {
  data: ChartDataPoint[];
}

const BiasMetricsChart: React.FC<Props> = ({ data }) => (
  <div className="card-wrapper chart-card sf-chart-card">
    <h2 className="card-title" style={{ display: 'none' }}>Fairness Thresholds Over Time</h2>
    <ResponsiveContainer width="100%" height="100%">
      <LineChart data={data}>
        <Tooltip
          contentStyle={{
            backgroundColor: 'rgba(11, 14, 20, 0.9)',
            backdropFilter: 'blur(20px)',
            borderColor: 'rgba(184, 242, 58, 0.15)',
            borderRadius: '12px',
            color: 'white',
            padding: '12px 16px',
            boxShadow: '0 8px 32px rgba(0,0,0,0.5)',
          }}
          itemStyle={{ color: 'white', fontFamily: 'Inter', fontSize: '0.82rem' }}
          labelStyle={{ color: '#9ca3af', fontFamily: 'JetBrains Mono', fontSize: '0.75rem' }}
        />
        <Legend wrapperStyle={{ fontFamily: 'Inter', fontSize: '0.82rem' }} />
        <Line
          type="monotone"
          dataKey="icd_score"
          name="Individual Disparity"
          stroke="#f59e0b"
          strokeWidth={2.5}
          dot={false}
          activeDot={{ r: 5, fill: '#f59e0b', stroke: '#050608', strokeWidth: 2 }}
          isAnimationActive={true}
          animationDuration={800}
          animationEasing="ease-out"
        />
        <Line
          type="monotone"
          dataKey="dpd_score"
          name="Demographic Parity"
          stroke="#10b981"
          strokeWidth={2.5}
          dot={false}
          activeDot={{ r: 5, fill: '#10b981', stroke: '#050608', strokeWidth: 2 }}
          isAnimationActive={true}
          animationDuration={800}
          animationEasing="ease-out"
        />
      </LineChart>
    </ResponsiveContainer>
  </div>
);

export default BiasMetricsChart;
