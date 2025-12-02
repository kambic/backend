<!-- JwtTool.vue -->
<template>
  <div class="p-4 max-w-xl mx-auto">
    <h1 class="text-2xl font-bold mb-4">JWT Decoder / Encoder</h1>

    <div class="mb-6">
      <label class="block font-semibold">JWT Token (for decode)</label>
      <textarea v-model="jwtInput" rows="3" class="textarea textarea-bordered w-full"></textarea>
      <button class="btn btn-primary mt-2" @click="decodeJwt">Decode</button>
    </div>

    <div v-if="decodedHeader || decodedPayload" class="mb-6">
      <div class="mb-4">
        <h2 class="font-semibold">Header</h2>
        <pre class="bg-base-200 p-2 rounded">{{ decodedHeader }}</pre>
      </div>
      <div>
        <h2 class="font-semibold">Payload</h2>
        <pre class="bg-base-200 p-2 rounded">{{ decodedPayload }}</pre>
      </div>
    </div>

    <hr class="my-6" />

    <div class="mb-6">
      <label class="block font-semibold">Header (JSON, for encoding)</label>
      <textarea v-model="encodeHeader" rows="3" class="textarea textarea-bordered w-full"></textarea>
    </div>
    <div class="mb-6">
      <label class="block font-semibold">Payload (JSON)</label>
      <textarea v-model="encodePayload" rows="5" class="textarea textarea-bordered w-full"></textarea>
    </div>
    <button class="btn btn-secondary" @click="encodeJwt">Encode</button>

    <div v-if="encodedJwt" class="mt-4">
      <h2 class="font-semibold">Resulting JWT</h2>
      <textarea readonly rows="2" class="textarea w-full">{{ encodedJwt }}</textarea>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue';

function base64UrlDecode(str) {
  // add padding if needed
  str = str.replace(/-/g, '+').replace(/_/g, '/');
  while (str.length % 4) str += '=';
  const decoded = atob(str);
  try {
    // for Unicode support
    return decodeURIComponent(escape(decoded));
  } catch {
    return decoded;
  }
}

function base64UrlEncode(str) {
  const encoded = btoa(unescape(encodeURIComponent(str)));
  return encoded.replace(/\+/g, '-').replace(/\//g, '_').replace(/=+$/, '');
}

const jwtInput = ref('');
const decodedHeader = ref('');
const decodedPayload = ref('');

const encodeHeader = ref(`{
  "alg": "HS256",
  "typ": "JWT"
}`);
const encodePayload = ref(`{
  "sub": "1234567890",
  "name": "John Doe",
  "iat": ${Math.floor(Date.now() / 1000)}
}`);
const encodedJwt = ref('');

function decodeJwt() {
  decodedHeader.value = '';
  decodedPayload.value = '';
  try {
    const parts = jwtInput.value.split('.');
    if (parts.length < 2) throw new Error('Not a valid JWT');
    const h = JSON.parse(base64UrlDecode(parts[0]));
    const p = JSON.parse(base64UrlDecode(parts[1]));
    decodedHeader.value = JSON.stringify(h, null, 2);
    decodedPayload.value = JSON.stringify(p, null, 2);
  } catch (err) {
    alert('Invalid JWT: ' + err);
  }
}

function encodeJwt() {
  try {
    const h = JSON.parse(encodeHeader.value);
    const p = JSON.parse(encodePayload.value);
    const part1 = base64UrlEncode(JSON.stringify(h));
    const part2 = base64UrlEncode(JSON.stringify(p));
    // Note: no signature — for demo only
    encodedJwt.value = `${part1}.${part2}.`;
  } catch (err) {
    alert('Invalid JSON: ' + err);
  }
}
</script>
