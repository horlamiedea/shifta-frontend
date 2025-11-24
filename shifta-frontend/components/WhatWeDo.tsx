"use client";

import { motion } from "framer-motion";
import { Stethoscope, Building2, Wallet, Clock } from "lucide-react";

const features = [
    {
        icon: <Stethoscope className="w-8 h-8 text-primary" />,
        title: "For Professionals",
        description: "Access thousands of shifts at top facilities. Set your own rates and schedule.",
    },
    {
        icon: <Building2 className="w-8 h-8 text-accent" />,
        title: "For Facilities",
        description: "Fill shifts instantly with verified professionals. No more staffing shortages.",
    },
    {
        icon: <Wallet className="w-8 h-8 text-green-500" />,
        title: "Instant Pay",
        description: "Get paid immediately after your shift is verified. No more waiting for weeks.",
    },
    {
        icon: <Clock className="w-8 h-8 text-yellow-500" />,
        title: "Total Control",
        description: "You decide when and where you work. Manage everything from our app.",
    },
];

export default function WhatWeDo() {
    return (
        <section className="py-24 bg-black/50 relative">
            <div className="container mx-auto px-6">
                <div className="text-center mb-16">
                    <h2 className="text-3xl md:text-5xl font-bold mb-4">What We Do</h2>
                    <p className="text-muted-foreground max-w-2xl mx-auto">
                        Shifta bridges the gap between healthcare professionals and facilities,
                        creating a seamless ecosystem for on-demand staffing.
                    </p>
                </div>

                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-8">
                    {features.map((feature, index) => (
                        <motion.div
                            key={index}
                            initial={{ opacity: 0, y: 20 }}
                            whileInView={{ opacity: 1, y: 0 }}
                            transition={{ duration: 0.5, delay: index * 0.1 }}
                            viewport={{ once: true }}
                            className="glass-card p-8 rounded-2xl hover:bg-white/5 transition-colors"
                        >
                            <div className="mb-6 p-4 bg-white/5 rounded-xl inline-block">
                                {feature.icon}
                            </div>
                            <h3 className="text-xl font-bold mb-3">{feature.title}</h3>
                            <p className="text-muted-foreground text-sm leading-relaxed">
                                {feature.description}
                            </p>
                        </motion.div>
                    ))}
                </div>
            </div>
        </section>
    );
}
