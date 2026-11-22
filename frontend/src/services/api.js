const BASE_URL = 'https://information-cascade-intelligence-api.onrender.com/api';

export async function fetchOverview() {
  const res = await fetch(`${BASE_URL}/overview`);
  if (!res.ok) throw new Error(`Overview fetch failed: ${res.statusText}`);
  return res.json();
}

export async function fetchTopics(limit = 60, sortBy = 'cascade') {
  const res = await fetch(`${BASE_URL}/topics?limit=${limit}&sort_by=${sortBy}`);
  if (!res.ok) throw new Error(`Topics fetch failed: ${res.statusText}`);
  return res.json();
}

export async function fetchSingleTopic(topicId) {
  const res = await fetch(`${BASE_URL}/topics/${encodeURIComponent(topicId)}`);
  if (!res.ok) throw new Error(`Topic fetch failed: ${res.statusText}`);
  return res.json();
}

export async function fetchNarrativeGraph(topicId) {
  const res = await fetch(`${BASE_URL}/narratives/${encodeURIComponent(topicId)}`);
  if (!res.ok) throw new Error(`Narrative graph fetch failed: ${res.statusText}`);
  return res.json();
}

export async function fetchAvailableNarratives() {
  const res = await fetch(`${BASE_URL}/narratives`);
  if (!res.ok) throw new Error(`Available narratives fetch failed: ${res.statusText}`);
  return res.json();
}

export async function fetchEvolution(topicId) {
  const res = await fetch(`${BASE_URL}/evolution/${encodeURIComponent(topicId)}`);
  if (!res.ok) throw new Error(`Evolution fetch failed: ${res.statusText}`);
  return res.json();
}

export async function fetchCascade(topicId) {
  const res = await fetch(`${BASE_URL}/cascades/${encodeURIComponent(topicId)}`);
  if (!res.ok) throw new Error(`Cascade fetch failed: ${res.statusText}`);
  return res.json();
}

export async function fetchAllCascades() {
  const res = await fetch(`${BASE_URL}/cascades`);
  if (!res.ok) throw new Error(`Cascades fetch failed: ${res.statusText}`);
  return res.json();
}

export async function fetchEvidence(topicId) {
  const res = await fetch(`${BASE_URL}/evidence/${encodeURIComponent(topicId)}`);
  if (!res.ok) throw new Error(`Evidence fetch failed: ${res.statusText}`);
  return res.json();
}

export async function fetchImpact(topicId) {
  const res = await fetch(`${BASE_URL}/impact/${encodeURIComponent(topicId)}`);
  if (!res.ok) throw new Error(`Impact fetch failed: ${res.statusText}`);
  return res.json();
}

export async function fetchPredictions(topicId) {
  const res = await fetch(`${BASE_URL}/predictions/${encodeURIComponent(topicId)}`);
  if (!res.ok) throw new Error(`Predictions fetch failed: ${res.statusText}`);
  return res.json();
}

export async function fetchMatrix() {
  const res = await fetch(`${BASE_URL}/matrix`);
  if (!res.ok) throw new Error(`Matrix fetch failed: ${res.statusText}`);
  return res.json();
}

export async function searchEcosystem(query = '', source = '', minScore = null) {
  let url = `${BASE_URL}/search?`;
  const params = new URLSearchParams();
  if (query) params.append('q', query);
  if (source) params.append('source', source);
  if (minScore !== null) params.append('min_score', minScore);
  const res = await fetch(url + params.toString());
  if (!res.ok) throw new Error(`Search failed: ${res.statusText}`);
  return res.json();
}

export async function compareTopics(topicA, topicB) {
  const res = await fetch(`${BASE_URL}/search/compare?topic_a=${encodeURIComponent(topicA)}&topic_b=${encodeURIComponent(topicB)}`);
  if (!res.ok) throw new Error(`Comparison failed: ${res.statusText}`);
  return res.json();
}

export async function triggerCollection() {
  const res = await fetch(`${BASE_URL}/collect`, { method: 'POST' });
  if (!res.ok) throw new Error(`Data collection trigger failed: ${res.statusText}`);
  return res.json();
}

export async function fetchArticles(limit = 100, source = '', search = '') {
  let url = `${BASE_URL}/articles?limit=${limit}`;
  if (source) url += `&source=${encodeURIComponent(source)}`;
  if (search) url += `&search=${encodeURIComponent(search)}`;
  const res = await fetch(url);
  if (!res.ok) throw new Error(`Articles fetch failed: ${res.statusText}`);
  return res.json();
}

export async function fetchSources() {
  const res = await fetch(`${BASE_URL}/sources`);
  if (!res.ok) throw new Error(`Sources fetch failed: ${res.statusText}`);
  return res.json();
}

export async function sendAgentMessage(prompt, topicId = null) {
  const res = await fetch(`${BASE_URL}/agent/chat`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ prompt, topic_id: topicId })
  });
  if (!res.ok) throw new Error(`Agent query failed: ${res.statusText}`);
  return res.json();
}

export async function fetchSourceCountries() {
  const res = await fetch(`${BASE_URL}/geography/source-countries`);
  if (!res.ok) throw new Error(`Fetch source countries failed`);
  return res.json();
}

export async function fetchEventCountries() {
  const res = await fetch(`${BASE_URL}/geography/event-countries`);
  if (!res.ok) throw new Error(`Fetch event countries failed`);
  return res.json();
}

export async function fetchTopicsByCountry(country, type = 'source') {
  const res = await fetch(`${BASE_URL}/geography/topics/${encodeURIComponent(country)}?type=${type}`);
  if (!res.ok) throw new Error(`Fetch country topics failed`);
  return res.json();
}

