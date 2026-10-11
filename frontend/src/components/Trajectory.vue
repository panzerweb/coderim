<script setup lang="ts">
import { computed } from 'vue'
import type { Attempt } from '../types'
const props = defineProps<{attempts: Attempt[]}>()
const ordered = computed(() => [...props.attempts].reverse().filter(a => a.result?.assessment?.complete))
const series = [{key: 'correctness', label: 'Correctness', color: '#c9f16d'}, {key: 'requirements', label: 'Requirements', color: '#79bbff'}, {key: 'final', label: 'Overall', color: '#d5a1ff'}] as const
function x(i: number) { return 40 + (ordered.value.length > 1 ? i * 600 / (ordered.value.length - 1) : 0) }
function y(value: number) { return 160 - value * 1.3 }
const plotted = computed(() => series.map(s => ({...s, points: ordered.value.map((a, i) => ({i, value: a.result!.assessment![s.key]}))})))
</script>

<template>
  <section class="trajectory" aria-label="Progress across attempts">
    <div class="section-heading"><h3>Your trajectory</h3><span>Same problem version & language · latest 200 attempts</span></div>
    <p v-if="!ordered.length" class="empty">Submit a solution to start your progress timeline.</p>
    <template v-else>
      <svg viewBox="0 0 680 200" role="img" aria-label="Scores across completed attempts, from zero to one hundred percent">
        <g v-for="n in [0, 50, 100]" :key="n"><line x1="40" x2="650" :y1="y(n)" :y2="y(n)" stroke="#2c373d"/><text x="3" :y="y(n) + 4" fill="#9aa6ad" font-size="12">{{ n }}</text></g>
        <g v-for="s in plotted" :key="s.key">
          <template v-for="(point, index) in s.points" :key="point.i">
            <line v-if="index > 0 && point.value !== null && s.points[index - 1]?.value != null" :x1="x(s.points[index - 1]!.i)" :y1="y(s.points[index - 1]!.value!)" :x2="x(point.i)" :y2="y(point.value!)" :stroke="s.color" stroke-width="2"/>
            <circle v-if="point.value !== null" :cx="x(point.i)" :cy="y(point.value!)" r="4" :fill="s.color"><title>{{ s.label }} · attempt {{ point.i + 1 }} · {{ point.value }}%</title></circle>
          </template>
        </g>
        <text x="40" y="190" fill="#9aa6ad" font-size="12">First displayed attempt</text><text x="640" y="190" text-anchor="end" fill="#9aa6ad" font-size="12">Latest</text>
      </svg>
      <div class="chart-legend"><span v-for="s in series" :key="s.key"><i :style="{background: s.color}"></i>{{ s.label }}</span></div>
      <p class="muted">{{ ordered.length }} complete assessments. Incomplete judging is excluded; overall scores appear after review.</p>
    </template>
  </section>
</template>
