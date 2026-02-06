"use client";

import React from 'react';
import {
    BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, Legend,
    LineChart, Line, ScatterChart, Scatter, PieChart, Pie, Cell,
    ResponsiveContainer
} from 'recharts';

interface ChartConfig {
    type: "bar" | "line" | "scatter" | "pie";
    title: string;
    x_key: string;
    y_key: string;
    data: any[];
}

interface ChartRendererProps {
    config: ChartConfig;
}

const COLORS = ['#0088FE', '#00C49F', '#FFBB28', '#FF8042', '#8884d8', '#82ca9d'];

export default function ChartRenderer({ config }: ChartRendererProps) {
    const { type, title, x_key, y_key, data } = config;

    // Common style for chart container
    const Container = ({ children }: { children: React.ReactNode }) => (
        <div className="w-full h-[300px] bg-white/5 rounded-lg p-4 border border-white/10 my-2">
            <h4 className="text-xs font-bold uppercase text-white/50 mb-2 text-center">{title}</h4>
            <div className="w-full h-[90%]">
                <ResponsiveContainer width="100%" height="100%">
                    {children}
                </ResponsiveContainer>
            </div>
        </div>
    );

    if (type === "bar") {
        return (
            <Container>
                <BarChart data={data}>
                    <CartesianGrid strokeDasharray="3 3" stroke="#ffffff10" />
                    <XAxis dataKey={x_key} stroke="#ffffff50" fontSize={10} />
                    <YAxis stroke="#ffffff50" fontSize={10} />
                    <Tooltip
                        contentStyle={{ backgroundColor: '#0d0d1a', borderColor: '#ffffff20', color: '#fff' }}
                        itemStyle={{ color: '#fff' }}
                    />
                    <Legend />
                    <Bar dataKey={y_key} fill="#8884d8" radius={[4, 4, 0, 0]} />
                </BarChart>
            </Container>
        );
    }

    if (type === "line") {
        return (
            <Container>
                <LineChart data={data}>
                    <CartesianGrid strokeDasharray="3 3" stroke="#ffffff10" />
                    <XAxis dataKey={x_key} stroke="#ffffff50" fontSize={10} />
                    <YAxis stroke="#ffffff50" fontSize={10} />
                    <Tooltip
                        contentStyle={{ backgroundColor: '#0d0d1a', borderColor: '#ffffff20', color: '#fff' }}
                    />
                    <Legend />
                    <Line type="monotone" dataKey={y_key} stroke="#82ca9d" strokeWidth={2} dot={{ r: 4 }} activeDot={{ r: 6 }} />
                </LineChart>
            </Container>
        );
    }

    if (type === "scatter") {
        return (
            <Container>
                <ScatterChart margin={{ top: 20, right: 20, bottom: 20, left: 20 }}>
                    <CartesianGrid stroke="#ffffff10" />
                    <XAxis type="category" dataKey={x_key} name="X" stroke="#ffffff50" fontSize={10} />
                    <YAxis type="number" dataKey={y_key} name="Y" stroke="#ffffff50" fontSize={10} />
                    <Tooltip cursor={{ strokeDasharray: '3 3' }} contentStyle={{ backgroundColor: '#0d0d1a', borderColor: '#ffffff20', color: '#fff' }} />
                    <Scatter name={title} data={data} fill="#8884d8" />
                </ScatterChart>
            </Container>
        );
    }

    if (type === "pie") {
        return (
            <Container>
                <PieChart>
                    <Pie
                        data={data}
                        cx="50%"
                        cy="50%"
                        innerRadius={60}
                        outerRadius={80}
                        fill="#8884d8"
                        paddingAngle={5}
                        dataKey={y_key}
                        nameKey={x_key}
                        label
                    >
                        {data.map((entry, index) => (
                            <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                        ))}
                    </Pie>
                    <Tooltip contentStyle={{ backgroundColor: '#0d0d1a', borderColor: '#ffffff20', color: '#fff' }} />
                    <Legend />
                </PieChart>
            </Container>
        );
    }

    return <div className="text-red-500 text-xs">Unsupported chart type: {type}</div>;
}
