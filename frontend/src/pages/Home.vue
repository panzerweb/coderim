<script setup lang="ts">
import { RouterLink } from 'vue-router'
import { clientState } from '../clientState'
</script>

<template>
  <main class="home page">
    <div class="eyebrow"><span class="tiny-line"></span> A WORKSPACE FOR BETTER SOLUTIONS</div>
    <section class="hero">
      <div class="hero-copy">
        <h1>Think it through.<br>Code it out.<br><em>Make it better.</em></h1>
        <p>Take on a problem, put your solution to the test, and see how it improves with every attempt.</p>
        <RouterLink :to="clientState.mode==='contest' ? (clientState.team?'/dashboard':'/join') : '/problems'" class="button primary large">{{ clientState.mode==='contest'?'Enter Code Relay':'Start practicing' }} <span>↗</span></RouterLink>
        <div class="hero-note">YOUR CODE. YOUR MACHINE. YOUR PROGRESS.</div>
      </div>
      <div class="hero-preview" aria-label="Example of a solution progress view">
        <div class="preview-top"><span class="window-dots">● ● ●</span><span>solution / next iteration</span></div>
        <div class="preview-code"><span class="line-no">01</span> <span class="code-purple">def</span> validate(source):<br><span class="line-no">02</span> &nbsp;&nbsp;stack = []<br><span class="line-no">03</span> &nbsp;&nbsp;quote = <span class="code-purple">None</span><br><span class="line-no">04</span> &nbsp;&nbsp;<span class="code-purple">for</span> char <span class="code-purple">in</span> source:<br><span class="line-no">05</span> &nbsp;&nbsp;&nbsp;&nbsp;<span class="code-muted"># one character at a time</span><br><span class="line-no">06</span> &nbsp;&nbsp;&nbsp;&nbsp;...</div>
        <div class="preview-result"><span class="success">✓ Accepted</span><span>All official tests passed</span></div>
        <div class="preview-chart"><div><span class="eyebrow">YOUR TRAJECTORY</span><strong>Every attempt counts.</strong></div><svg viewBox="0 0 240 100" aria-hidden="true"><path d="M5 90 L55 72 L105 73 L155 35 L205 10 L235 10" fill="none" stroke="#c9f16d" stroke-width="3"/><circle cx="205" cy="10" r="4" fill="#c9f16d"/></svg></div>
        <span class="preview-label">ILLUSTRATIVE WORKSPACE</span>
      </div>
    </section>
    <section class="steps" aria-label="How it works">
      <article><span>01 / EXPLORE</span><h2>Pick your challenge.</h2><p>Read the requirements and understand what a correct solution needs to do.</p></article>
      <article><span>02 / BUILD</span><h2>Find your approach.</h2><p>Write a complete program. Try the samples and your own edge cases.</p></article>
      <article><span>03 / IMPROVE</span><h2>Follow your progress.</h2><p>Submit, review the evidence, and refine your solution across attempts.</p></article>
    </section>
    <aside class="practice-note">{{ clientState.mode==='contest'?'Join with your organizer-provided team code. Official attempts and feedback are private to your team. Test results are calculated automatically; organizers review code quality.':'Local practice runs your programs on this computer. Use code you trust. Human reviews assess clarity and technical quality separately from test results.' }}</aside>
  </main>
</template>
