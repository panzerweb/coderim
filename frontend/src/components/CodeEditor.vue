<script setup lang="ts">
import { onMounted, onBeforeUnmount, ref, watch } from 'vue'
import * as monaco from 'monaco-editor/esm/vs/editor/editor.api'
import 'monaco-editor/esm/vs/basic-languages/python/python.contribution'
import 'monaco-editor/esm/vs/basic-languages/cpp/cpp.contribution'
import 'monaco-editor/esm/vs/basic-languages/java/java.contribution'
import 'monaco-editor/esm/vs/language/typescript/monaco.contribution'
import EditorWorker from 'monaco-editor/esm/vs/editor/editor.worker?worker'
import TsWorker from 'monaco-editor/esm/vs/language/typescript/ts.worker?worker'

const props = defineProps<{modelValue: string; language: string; readonly?: boolean}>()
const emit = defineEmits<{ 'update:modelValue': [value: string] }>()
const host = ref<HTMLElement>()
let editor: monaco.editor.IStandaloneCodeEditor | undefined
let subscription: monaco.IDisposable | undefined
let model: monaco.editor.ITextModel | undefined
let applying = false

;(globalThis as typeof globalThis & {MonacoEnvironment: unknown}).MonacoEnvironment = {
  getWorker(_: string, label: string) { return label === 'typescript' || label === 'javascript' ? new TsWorker() : new EditorWorker() },
}
onMounted(() => {
  monaco.editor.defineTheme('relay', {base: 'vs-dark', inherit: true, rules: [], colors: {
    'editor.background': '#141a1e', 'editorLineNumber.foreground': '#546068', 'editorGutter.background': '#141a1e',
    'editor.lineHighlightBackground': '#1c252a', 'editor.selectionBackground': '#334638',
  }})
  model = monaco.editor.createModel(props.modelValue, props.language)
  editor = monaco.editor.create(host.value!, {model, theme: 'relay', fontSize: 14, lineHeight: 24,
    fontFamily: 'Consolas, "Courier New", monospace', minimap: {enabled: false}, automaticLayout: true,
    scrollBeyondLastLine: false, padding: {top: 16}, tabSize: 4, readOnly: props.readonly,
    accessibilitySupport: 'on', ariaLabel: 'Solution code editor', fixedOverflowWidgets: true})
  subscription = editor.onDidChangeModelContent(() => { if (!applying) emit('update:modelValue', editor!.getValue()) })
})
watch(() => props.modelValue, value => {
  if (editor && editor.getValue() !== value) { applying = true; editor.setValue(value); applying = false }
})
watch(() => props.language, value => { if (model) monaco.editor.setModelLanguage(model, value) })
watch(() => props.readonly, value => editor?.updateOptions({readOnly: value}))
onBeforeUnmount(() => { subscription?.dispose(); editor?.dispose(); model?.dispose() })
</script>

<template><div ref="host" class="code-editor" data-testid="code-editor"></div></template>
