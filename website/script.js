document.addEventListener('DOMContentLoaded', () => {
    // Optional: Add some simple entrance animations
    const cards = document.querySelectorAll('.stat-card, .step-card, .team-card');
    cards.forEach((card, index) => {
        card.style.opacity = '0';
        card.style.animation = `fadeInUp 0.5s ease forwards ${index * 0.1}s`;
    });
});

// Keyframes for fade in (injected via JS for simplicity or could be in CSS)
const styleSheet = document.createElement("style");
styleSheet.innerText = `
@keyframes fadeInUp {
    from {
        opacity: 0;
        transform: translateY(20px);
    }
    to {
        opacity: 1;
        transform: translateY(0);
    }
}
`;
document.head.appendChild(styleSheet);
