<script setup lang="ts">
import type { ReferenceComplexity, ReviewedComplexity } from '../types'
defineProps<{reference?: ReferenceComplexity | null; analysis?: ReviewedComplexity | null}>()
</script>

<template>
  <section class="complexity-analysis" aria-label="Complexity analysis">
    <h3>Time & space complexity</h3>
    <p class="muted">Big-O describes growth with input size. Execution time is a measurement, not an inferred complexity bound. These annotations do not change acceptance or calculate a separate score.</p>
    <div class="complexity-reviewed" aria-label="Reviewed complexity">
      <h4>Reviewed complexity <span>HUMAN ASSESSMENT OF SAVED SOURCE</span></h4>
      <p v-if="!analysis" class="muted">Not assessed. No complexity has been assigned to this program.</p>
      <template v-else>
        <p v-if="analysis.status === 'unable_to_assess'"><strong>Unable to assess</strong></p>
        <dl v-else class="complexity-bounds">
          <dt>Worst-case time</dt><dd>{{ analysis.worst_case_time }}</dd>
          <dt>Auxiliary space</dt><dd>{{ analysis.auxiliary_space }}</dd>
          <dt>Space including stored input/output</dt><dd>{{ analysis.total_space }}</dd>
        </dl>
        <p class="complexity-reasoning">{{ analysis.reasoning }}</p>
      </template>
    </div>
    <details class="complexity-reference" aria-label="Reference complexity targets">
      <summary>Reference targets <small>Challenge guidance, not the submitted code’s analysis</small></summary>
      <template v-if="reference">
        <dl class="complexity-bounds"><template v-for="(meaning, variable) in reference.variables" :key="variable"><dt>{{ variable }}</dt><dd>{{ meaning }}</dd></template></dl>
        <dl class="complexity-bounds"><template v-for="(bound, phase) in reference.time_by_phase" :key="phase"><dt>{{ phase }}</dt><dd>{{ bound }}</dd></template><dt>Auxiliary space</dt><dd>{{ reference.auxiliary_space }}</dd></dl>
        <p class="muted">{{ reference.notes }}</p>
      </template>
      <p v-else class="muted">No reference context was saved with this attempt. Historical attempts are not filled from the latest problem metadata.</p>
    </details>
  </section>
</template>
