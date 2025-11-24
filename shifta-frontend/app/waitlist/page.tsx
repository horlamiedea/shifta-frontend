import Navbar from "@/components/Navbar";
import Footer from "@/components/Footer";
import WaitlistForm from "@/components/WaitlistForm";

export default function WaitlistPage() {
    return (
        <main className="min-h-screen bg-background text-foreground selection:bg-primary selection:text-white flex flex-col">
            <Navbar />
            <div className="flex-grow flex items-center justify-center py-24 px-6 relative overflow-hidden">
                {/* Background Elements */}
                <div className="absolute inset-0 bg-[radial-gradient(ellipse_at_top,_var(--tw-gradient-stops))] from-primary/10 via-background to-background z-0" />
                <div className="absolute top-0 right-0 w-96 h-96 bg-accent/20 rounded-full blur-3xl opacity-20" />

                <div className="relative z-10 w-full">
                    <WaitlistForm />
                </div>
            </div>
            <Footer />
        </main>
    );
}
