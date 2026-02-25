import React from "react";
import Layout from "@theme/Layout";
import styles from "./guide.module.css";

const FLOW_STEPS = [
  { icon: "\uD83D\uDCD6", label: "Read the Lesson" },
  { icon: "\uD83C\uDCCF", label: "Review Flashcards" },
  { icon: "\uD83D\uDEE0\uFE0F", label: "Practice Exercises" },
  { icon: "\uD83C\uDFAF", label: "Take the Quiz" },
  { icon: "\uD83C\uDFC6", label: "Climb the Leaderboard" },
];

export default function GuidePage() {
  return (
    <Layout title="Study Guide">
      <div className={styles.container}>
        {/* Hero */}
        <header className={styles.hero}>
          <h1 className={styles.heroTitle}>Your Learning Toolkit</h1>
          <p className={styles.heroSubtitle}>
            Each lesson comes with study tools designed to help you truly learn
            the material — not just read it. Here's the learning flow and how
            each tool helps you retain what you study.
          </p>
        </header>

        {/* Flow visual */}
        <div className={styles.flow}>
          {FLOW_STEPS.map((step, i) => (
            <React.Fragment key={step.label}>
              <div className={styles.flowStep}>
                <span className={styles.flowIcon}>{step.icon}</span>
                {step.label}
              </div>
              {i < FLOW_STEPS.length - 1 && (
                <span className={styles.flowArrow} aria-hidden="true">
                  &#8595;
                </span>
              )}
            </React.Fragment>
          ))}
        </div>

        {/* Flashcards section */}
        <section id="flashcards" className={styles.section}>
          <h2 className={styles.sectionTitle}>Flashcards</h2>

          <p className={styles.sectionIntro}>
            Every lesson includes flashcards that help you actually{" "}
            <strong>remember</strong> what you read — not just recognize it in
            the moment. Here's why they work and how to get the most out of
            them.
          </p>

          {/* WHY — the science */}
          <h3 className={styles.subsectionTitle}>Why Flashcards Work</h3>
          <div className={styles.cardGrid}>
            <div className={styles.card}>
              <div className={styles.cardTitle}>
                <span aria-hidden="true">&#129504;</span> Active Recall
              </div>
              <div className={styles.cardBody}>
                Trying to answer before flipping the card forces your brain to{" "}
                <strong>retrieve</strong> — not just recognize. That effort is
                what makes the memory stick.
              </div>
            </div>

            <div className={styles.card}>
              <div className={styles.cardTitle}>
                <span aria-hidden="true">&#128257;</span> Spaced Repetition
              </div>
              <div className={styles.cardBody}>
                Cards you miss come back sooner. Cards you know space out
                further. Over time, this moves knowledge into{" "}
                <strong>long-term memory</strong> with less total study time.
              </div>
            </div>

            <div className={styles.card}>
              <div className={styles.cardTitle}>
                <span aria-hidden="true">&#127919;</span> One Idea Per Card
              </div>
              <div className={styles.cardBody}>
                Each card targets a single concept — one definition, one
                distinction, one principle. Small pieces are easier to learn
                than an entire lesson at once.
              </div>
            </div>

            <div className={styles.card}>
              <div className={styles.cardTitle}>
                <span aria-hidden="true">&#128200;</span> Self-Testing
              </div>
              <div className={styles.cardBody}>
                If you can answer without peeking, you know it. If you can't,
                you've found exactly what to focus on. No more guessing what
                you "think" you know.
              </div>
            </div>
          </div>

          {/* HOW — using our flashcards */}
          <h3 className={styles.subsectionTitle}>How to Use Them</h3>
          <div className={styles.cardGrid}>
            <div className={styles.card}>
              <div className={styles.cardTitle}>
                <span aria-hidden="true">&#128260;</span> Flip &amp; Rate
              </div>
              <div className={styles.cardBody}>
                Read the front. Try to answer in your head.{" "}
                <strong>Then</strong> flip the card to check. Rate yourself
                honestly: <strong>Missed It</strong> if you didn't recall the
                answer, <strong>Got It</strong> if you did. Honest ratings are
                the key — they tell the system what to show you next.
              </div>
            </div>

            <div className={styles.card}>
              <div className={styles.cardTitle}>
                <span aria-hidden="true">&#128161;</span> Tips for Best Results
              </div>
              <div className={styles.cardBody}>
                Review flashcards <strong>right after reading</strong> the
                lesson, while the material is fresh. Don't skip the ones you
                think you know — they go faster anyway. Come back the next day
                for a second pass; that's when spaced repetition really kicks
                in.
              </div>
            </div>

            <div className={styles.card}>
              <div className={styles.cardTitle}>
                <span aria-hidden="true">&#9000;</span> Keyboard Shortcuts
              </div>
              <div className={styles.cardBody}>
                <kbd>Space</kbd> flips the card. <kbd>1</kbd> rates "Missed It"
                and <kbd>2</kbd> rates "Got It". Use <kbd>&#8592;</kbd>{" "}
                <kbd>&#8594;</kbd> arrows to navigate between cards. Press{" "}
                <kbd>Esc</kbd> to exit fullscreen mode.
              </div>
            </div>

            <div className={styles.card}>
              <div className={styles.cardTitle}>
                <span aria-hidden="true">&#128229;</span> Download &amp; Export
              </div>
              <div className={styles.cardBody}>
                Want to study offline? Use the <strong>Download</strong> button
                on any flashcard deck to export as CSV (for any app) or as an
                Anki deck (.apkg) if available. Anki is a free app that
                supercharges spaced repetition across all your devices.
              </div>
            </div>
          </div>
        </section>
      </div>
    </Layout>
  );
}
