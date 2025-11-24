export default function Footer() {
    return (
        <footer className="py-12 border-t border-white/10 bg-black">
            <div className="container mx-auto px-6 text-center">
                <div className="flex items-center justify-center gap-2 mb-8">
                    <div className="w-6 h-6 bg-primary rounded-md flex items-center justify-center">
                        <span className="text-white font-bold text-sm">S</span>
                    </div>
                    <span className="text-lg font-bold text-white">Shifta</span>
                </div>
                <p className="text-muted-foreground text-sm mb-8">
                    &copy; {new Date().getFullYear()} Shifta. All rights reserved.
                </p>
                <div className="flex justify-center gap-6 text-sm text-muted-foreground">
                    <a href="#" className="hover:text-white transition-colors">Privacy Policy</a>
                    <a href="#" className="hover:text-white transition-colors">Terms of Service</a>
                    <a href="#" className="hover:text-white transition-colors">Contact</a>
                </div>
            </div>
        </footer>
    );
}
