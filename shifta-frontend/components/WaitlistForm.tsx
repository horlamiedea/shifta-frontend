"use client";

import { useState, ChangeEvent, FormEvent } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { Button } from "@/components/ui/button";
import { Upload, Check, ChevronRight, ChevronLeft, MapPin, DollarSign, FileText, User, Mail, Phone, Briefcase, Clock } from "lucide-react";
import { useRouter } from "next/navigation";

const MEDICAL_TYPES = [
    {
        category: "Nurses",
        types: [
            "Registered Nurse (General)",
            "ICU Nurse",
            "Paediatric Nurse",
            "Theatre / Perioperative Nurse",
            "Emergency Room (ER) Nurse",
            "Midwife",
            "Mental Health Nurse",
            "Neonatal ICU (NICU) Nurse",
            "Community Health Nurse",
            "Orthopedic Nurse"
        ]
    },
    {
        category: "Doctors",
        types: [
            "General Practitioner (GP)",
            "Emergency Physician",
            "Surgeon (General)",
            "Paediatrician",
            "Obstetrician / Gynecologist",
            "Anesthesiologist",
            "Cardiologist",
            "Internal Medicine Physician"
        ]
    },
    {
        category: "Pharmacists",
        types: [
            "Pharmacist",
            "Pharmacy Technician"
        ]
    },
    {
        category: "Allied Health",
        types: [
            "Medical Laboratory Scientist",
            "Radiographer / Radiologic Technologist",
            "Physiotherapist",
            "Occupational Therapist",
            "Dietitian / Nutritionist"
        ]
    }
];

export default function WaitlistForm() {
    const router = useRouter();
    const [step, setStep] = useState(1);
    const [loading, setLoading] = useState(false);
    const [success, setSuccess] = useState(false);

    const [formData, setFormData] = useState({
        full_name: "",
        email: "",
        phone_number: "",
        medical_type: "",
        years_of_experience: "",
        shift_rate_9hr: "",
        location: "",
        preferred_work_address: "",
        bio_data: "",
    });

    const [files, setFiles] = useState<{ cv_file: File | null; license_file: File | null }>({
        cv_file: null,
        license_file: null,
    });

    const handleChange = (e: ChangeEvent<HTMLInputElement | HTMLTextAreaElement | HTMLSelectElement>) => {
        const { name, value } = e.target;
        setFormData((prev) => ({ ...prev, [name]: value }));
    };

    const handleFileChange = (e: ChangeEvent<HTMLInputElement>, field: "cv_file" | "license_file") => {
        if (e.target.files && e.target.files[0]) {
            setFiles((prev) => ({ ...prev, [field]: e.target.files![0] }));
        }
    };

    const handleSubmit = async (e: FormEvent) => {
        e.preventDefault();
        setLoading(true);

        try {
            const data = new FormData();
            Object.entries(formData).forEach(([key, value]) => {
                data.append(key, value);
            });
            if (files.cv_file) data.append("cv_file", files.cv_file);
            if (files.license_file) data.append("license_file", files.license_file);

            const response = await fetch(`${process.env.NEXT_PUBLIC_API_URL}/auth/waitlist/`, {
                method: "POST",
                body: data,
            });

            if (response.ok) {
                setSuccess(true);
            } else {
                const errorData = await response.json();
                alert(`Error: ${JSON.stringify(errorData)}`);
            }
        } catch (error) {
            console.error("Error submitting form:", error);
            alert("An error occurred. Please try again.");
        } finally {
            setLoading(false);
        }
    };

    const nextStep = () => setStep((prev) => Math.min(prev + 1, 3));
    const prevStep = () => setStep((prev) => Math.max(prev - 1, 1));

    if (success) {
        return (
            <div className="text-center p-10 glass-card rounded-2xl max-w-md mx-auto">
                <div className="w-20 h-20 bg-green-500/20 rounded-full flex items-center justify-center mx-auto mb-6">
                    <Check className="w-10 h-10 text-green-500" />
                </div>
                <h2 className="text-3xl font-bold mb-4">You're on the list!</h2>
                <p className="text-muted-foreground mb-8">
                    Thanks for joining Shifta. We'll be in touch soon to verify your profile and get you started.
                </p>
                <Button onClick={() => router.push("/")} variant="outline">
                    Back to Home
                </Button>
            </div>
        );
    }

    return (
        <div className="w-full max-w-2xl mx-auto glass-card rounded-2xl p-8 md:p-12">
            <div className="mb-8">
                <div className="flex items-center justify-between mb-4">
                    <h2 className="text-2xl font-bold">Join the Waitlist</h2>
                    <span className="text-sm text-muted-foreground">Step {step} of 3</span>
                </div>
                <div className="h-2 bg-secondary rounded-full overflow-hidden">
                    <motion.div
                        className="h-full bg-primary"
                        initial={{ width: 0 }}
                        animate={{ width: `${(step / 3) * 100}%` }}
                        transition={{ duration: 0.3 }}
                    />
                </div>
            </div>

            <form onSubmit={handleSubmit}>
                <AnimatePresence mode="wait">
                    {step === 1 && (
                        <motion.div
                            key="step1"
                            initial={{ opacity: 0, x: 20 }}
                            animate={{ opacity: 1, x: 0 }}
                            exit={{ opacity: 0, x: -20 }}
                            className="space-y-6"
                        >
                            <div className="space-y-2">
                                <label className="text-sm font-medium flex items-center gap-2">
                                    <User className="w-4 h-4 text-primary" /> Full Name
                                </label>
                                <input
                                    type="text"
                                    name="full_name"
                                    value={formData.full_name}
                                    onChange={handleChange}
                                    className="w-full bg-black/20 border border-white/10 rounded-lg px-4 py-3 focus:outline-none focus:ring-2 focus:ring-primary transition-all"
                                    placeholder="John Doe"
                                    required
                                />
                            </div>
                            <div className="space-y-2">
                                <label className="text-sm font-medium flex items-center gap-2">
                                    <Mail className="w-4 h-4 text-primary" /> Email Address
                                </label>
                                <input
                                    type="email"
                                    name="email"
                                    value={formData.email}
                                    onChange={handleChange}
                                    className="w-full bg-black/20 border border-white/10 rounded-lg px-4 py-3 focus:outline-none focus:ring-2 focus:ring-primary transition-all"
                                    placeholder="john@example.com"
                                    required
                                />
                            </div>
                            <div className="space-y-2">
                                <label className="text-sm font-medium flex items-center gap-2">
                                    <Phone className="w-4 h-4 text-primary" /> Phone Number
                                </label>
                                <input
                                    type="tel"
                                    name="phone_number"
                                    value={formData.phone_number}
                                    onChange={handleChange}
                                    className="w-full bg-black/20 border border-white/10 rounded-lg px-4 py-3 focus:outline-none focus:ring-2 focus:ring-primary transition-all"
                                    placeholder="+234..."
                                    required
                                />
                            </div>
                        </motion.div>
                    )}

                    {step === 2 && (
                        <motion.div
                            key="step2"
                            initial={{ opacity: 0, x: 20 }}
                            animate={{ opacity: 1, x: 0 }}
                            exit={{ opacity: 0, x: -20 }}
                            className="space-y-6"
                        >
                            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                                <div className="space-y-2">
                                    <label className="text-sm font-medium flex items-center gap-2">
                                        <Briefcase className="w-4 h-4 text-primary" /> Medical Type
                                    </label>
                                    <select
                                        name="medical_type"
                                        value={formData.medical_type}
                                        onChange={handleChange}
                                        className="w-full bg-black/20 border border-white/10 rounded-lg px-4 py-3 focus:outline-none focus:ring-2 focus:ring-primary transition-all appearance-none"
                                        required
                                    >
                                        <option value="" className="bg-black">Select Type</option>
                                        {MEDICAL_TYPES.map((category) => (
                                            <optgroup key={category.category} label={category.category} className="bg-black text-white">
                                                {category.types.map((type) => (
                                                    <option key={type} value={type} className="bg-black text-white">
                                                        {type}
                                                    </option>
                                                ))}
                                            </optgroup>
                                        ))}
                                    </select>
                                </div>
                                <div className="space-y-2">
                                    <label className="text-sm font-medium flex items-center gap-2">
                                        <Clock className="w-4 h-4 text-primary" /> Years of Experience
                                    </label>
                                    <input
                                        type="number"
                                        name="years_of_experience"
                                        value={formData.years_of_experience}
                                        onChange={handleChange}
                                        className="w-full bg-black/20 border border-white/10 rounded-lg px-4 py-3 focus:outline-none focus:ring-2 focus:ring-primary transition-all"
                                        placeholder="e.g. 5"
                                        required
                                    />
                                </div>
                            </div>

                            <div className="space-y-2">
                                <label className="text-sm font-medium flex items-center gap-2">
                                    <DollarSign className="w-4 h-4 text-primary" /> Expected Rate (9hr Shift)
                                </label>
                                <input
                                    type="number"
                                    name="shift_rate_9hr"
                                    value={formData.shift_rate_9hr}
                                    onChange={handleChange}
                                    className="w-full bg-black/20 border border-white/10 rounded-lg px-4 py-3 focus:outline-none focus:ring-2 focus:ring-primary transition-all"
                                    placeholder="Amount in NGN"
                                    required
                                />
                            </div>

                            <div className="space-y-2">
                                <label className="text-sm font-medium flex items-center gap-2">
                                    <FileText className="w-4 h-4 text-primary" /> Bio / Summary
                                </label>
                                <textarea
                                    name="bio_data"
                                    value={formData.bio_data}
                                    onChange={handleChange}
                                    className="w-full bg-black/20 border border-white/10 rounded-lg px-4 py-3 focus:outline-none focus:ring-2 focus:ring-primary transition-all min-h-[100px]"
                                    placeholder="Tell us a bit about yourself..."
                                />
                            </div>
                        </motion.div>
                    )}

                    {step === 3 && (
                        <motion.div
                            key="step3"
                            initial={{ opacity: 0, x: 20 }}
                            animate={{ opacity: 1, x: 0 }}
                            exit={{ opacity: 0, x: -20 }}
                            className="space-y-6"
                        >
                            <div className="space-y-2">
                                <label className="text-sm font-medium flex items-center gap-2">
                                    <MapPin className="w-4 h-4 text-primary" /> Current Location
                                </label>
                                <input
                                    type="text"
                                    name="location"
                                    value={formData.location}
                                    onChange={handleChange}
                                    className="w-full bg-black/20 border border-white/10 rounded-lg px-4 py-3 focus:outline-none focus:ring-2 focus:ring-primary transition-all"
                                    placeholder="City, State"
                                    required
                                />
                            </div>

                            <div className="space-y-2">
                                <label className="text-sm font-medium flex items-center gap-2">
                                    <MapPin className="w-4 h-4 text-primary" /> Preferred Work Areas
                                </label>
                                <input
                                    type="text"
                                    name="preferred_work_address"
                                    value={formData.preferred_work_address}
                                    onChange={handleChange}
                                    className="w-full bg-black/20 border border-white/10 rounded-lg px-4 py-3 focus:outline-none focus:ring-2 focus:ring-primary transition-all"
                                    placeholder="e.g. Lekki, Ikeja, VI"
                                />
                            </div>

                            <div className="grid grid-cols-1 md:grid-cols-2 gap-6 pt-4">
                                <div className="space-y-2">
                                    <label className="block text-sm font-medium mb-2">Upload CV</label>
                                    <div className="relative group">
                                        <input
                                            type="file"
                                            onChange={(e) => handleFileChange(e, "cv_file")}
                                            className="absolute inset-0 w-full h-full opacity-0 cursor-pointer z-10"
                                            accept=".pdf,.doc,.docx"
                                        />
                                        <div className="bg-black/20 border border-dashed border-white/20 rounded-lg p-6 text-center group-hover:border-primary transition-colors">
                                            <Upload className="w-8 h-8 mx-auto mb-2 text-muted-foreground group-hover:text-primary transition-colors" />
                                            <p className="text-sm text-muted-foreground">
                                                {files.cv_file ? files.cv_file.name : "Click to upload CV"}
                                            </p>
                                        </div>
                                    </div>
                                </div>

                                <div className="space-y-2">
                                    <label className="block text-sm font-medium mb-2">Upload License</label>
                                    <div className="relative group">
                                        <input
                                            type="file"
                                            onChange={(e) => handleFileChange(e, "license_file")}
                                            className="absolute inset-0 w-full h-full opacity-0 cursor-pointer z-10"
                                            accept=".pdf,.jpg,.png"
                                        />
                                        <div className="bg-black/20 border border-dashed border-white/20 rounded-lg p-6 text-center group-hover:border-primary transition-colors">
                                            <Upload className="w-8 h-8 mx-auto mb-2 text-muted-foreground group-hover:text-primary transition-colors" />
                                            <p className="text-sm text-muted-foreground">
                                                {files.license_file ? files.license_file.name : "Click to upload License"}
                                            </p>
                                        </div>
                                    </div>
                                </div>
                            </div>
                        </motion.div>
                    )}
                </AnimatePresence>

                <div className="flex justify-between mt-8 pt-6 border-t border-white/10">
                    {step > 1 ? (
                        <Button type="button" variant="outline" onClick={prevStep}>
                            <ChevronLeft className="w-4 h-4 mr-2" /> Back
                        </Button>
                    ) : (
                        <div />
                    )}

                    {step < 3 ? (
                        <Button type="button" onClick={nextStep} variant="premium">
                            Next Step <ChevronRight className="w-4 h-4 ml-2" />
                        </Button>
                    ) : (
                        <Button type="submit" variant="premium" disabled={loading}>
                            {loading ? "Submitting..." : "Join Waitlist"}
                        </Button>
                    )}
                </div>
            </form>
        </div>
    );
}
