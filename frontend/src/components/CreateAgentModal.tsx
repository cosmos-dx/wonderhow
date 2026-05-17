"use client";

import { useState, useEffect } from "react";
import { api, Group, CreateAgentPayload } from "@/lib/api";

interface Props {
  onClose: () => void;
  onCreated: () => void;
}

const TEMPERAMENTS = ["calm", "passionate", "balanced", "aggressive", "diplomatic"];
const POLITICAL_BIASES = ["left-leaning", "centrist", "right-leaning", "libertarian", "progressive"];
const WRITING_STYLES = ["conversational", "formal", "sarcastic", "poetic", "intellectual", "slang-heavy"];

export default function CreateAgentModal({ onClose, onCreated }: Props) {
  const [groups, setGroups] = useState<Group[]>([]);
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState("");

  const [name, setName] = useState("");
  const [age, setAge] = useState(25);
  const [profession, setProfession] = useState("");
  const [background, setBackground] = useState("");
  const [politicalBias, setPoliticalBias] = useState("centrist");
  const [temperament, setTemperament] = useState("balanced");
  const [interests, setInterests] = useState("");
  const [writingStyle, setWritingStyle] = useState("conversational");
  const [stubbornness, setStubbornness] = useState(0.5);
  const [curiosity, setCuriosity] = useState(0.5);
  const [aggressiveness, setAggressiveness] = useState(0.3);
  const [humor, setHumor] = useState(0.3);
  const [beliefs, setBeliefs] = useState("");
  const [groupSlug, setGroupSlug] = useState("");

  useEffect(() => {
    api.getGroups().then((g) => {
      setGroups(g);
      if (g.length > 0) setGroupSlug(g[0].slug);
    });
  }, []);

  const handleSubmit = async () => {
    if (!name.trim()) { setError("Name is required"); return; }
    if (!groupSlug) { setError("Select a group"); return; }

    setSubmitting(true);
    setError("");

    const coreBeliefs: Record<string, string> = {};
    beliefs.split("\n").filter(Boolean).forEach((line) => {
      const [topic, ...stanceParts] = line.split(":");
      if (topic && stanceParts.length) {
        coreBeliefs[topic.trim()] = stanceParts.join(":").trim();
      }
    });

    const payload: CreateAgentPayload = {
      name: name.trim(),
      age,
      profession,
      background,
      political_bias: politicalBias,
      temperament,
      interests: interests.split(",").map((i) => i.trim()).filter(Boolean),
      writing_style: writingStyle,
      stubbornness,
      curiosity,
      aggressiveness,
      humor,
      core_beliefs: coreBeliefs,
      group_slug: groupSlug,
    };

    try {
      await api.createAgent(payload);
      onCreated();
      onClose();
    } catch {
      setError("Failed to create agent. Check console for details.");
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/60 backdrop-blur-sm p-4">
      <div className="w-full max-w-2xl max-h-[90vh] overflow-y-auto rounded-2xl border border-[#2a2a4a] bg-[#12121a] shadow-2xl">
        <div className="sticky top-0 z-10 flex items-center justify-between border-b border-[#2a2a4a] bg-[#12121a] px-6 py-4">
          <h2 className="text-lg font-bold bg-gradient-to-r from-[#4f8aff] to-[#8b5cf6] bg-clip-text text-transparent">
            Create New Agent
          </h2>
          <button onClick={onClose} className="text-[#9393b0] hover:text-white text-xl leading-none">
            &times;
          </button>
        </div>

        <div className="space-y-5 px-6 py-5">
          {/* Identity */}
          <section>
            <h3 className="text-sm font-semibold text-[#e4e4ef] mb-3">Identity</h3>
            <div className="grid grid-cols-2 gap-3">
              <div className="col-span-2 sm:col-span-1">
                <label className="block text-xs text-[#9393b0] mb-1">Name *</label>
                <input
                  value={name}
                  onChange={(e) => setName(e.target.value)}
                  placeholder="e.g. Priya Sharma"
                  className="w-full rounded-lg border border-[#2a2a4a] bg-[#0a0a0f] px-3 py-2 text-sm text-[#e4e4ef] placeholder-[#9393b0]/40 outline-none focus:border-[#4f8aff]/50"
                />
              </div>
              <div>
                <label className="block text-xs text-[#9393b0] mb-1">Age</label>
                <input
                  type="number"
                  value={age}
                  onChange={(e) => setAge(Number(e.target.value))}
                  min={16}
                  max={90}
                  className="w-full rounded-lg border border-[#2a2a4a] bg-[#0a0a0f] px-3 py-2 text-sm text-[#e4e4ef] outline-none focus:border-[#4f8aff]/50"
                />
              </div>
              <div>
                <label className="block text-xs text-[#9393b0] mb-1">Profession</label>
                <input
                  value={profession}
                  onChange={(e) => setProfession(e.target.value)}
                  placeholder="e.g. Software Engineer"
                  className="w-full rounded-lg border border-[#2a2a4a] bg-[#0a0a0f] px-3 py-2 text-sm text-[#e4e4ef] placeholder-[#9393b0]/40 outline-none focus:border-[#4f8aff]/50"
                />
              </div>
              <div className="col-span-2">
                <label className="block text-xs text-[#9393b0] mb-1">Background</label>
                <textarea
                  value={background}
                  onChange={(e) => setBackground(e.target.value)}
                  placeholder="Brief backstory... e.g. Grew up in Delhi, studied at IIT, passionate about open source"
                  rows={2}
                  className="w-full rounded-lg border border-[#2a2a4a] bg-[#0a0a0f] px-3 py-2 text-sm text-[#e4e4ef] placeholder-[#9393b0]/40 outline-none focus:border-[#4f8aff]/50 resize-none"
                />
              </div>
            </div>
          </section>

          {/* Personality */}
          <section>
            <h3 className="text-sm font-semibold text-[#e4e4ef] mb-3">Personality</h3>
            <div className="grid grid-cols-2 gap-3">
              <div>
                <label className="block text-xs text-[#9393b0] mb-1">Temperament</label>
                <select
                  value={temperament}
                  onChange={(e) => setTemperament(e.target.value)}
                  className="w-full rounded-lg border border-[#2a2a4a] bg-[#0a0a0f] px-3 py-2 text-sm text-[#e4e4ef] outline-none focus:border-[#4f8aff]/50"
                >
                  {TEMPERAMENTS.map((t) => (
                    <option key={t} value={t}>{t}</option>
                  ))}
                </select>
              </div>
              <div>
                <label className="block text-xs text-[#9393b0] mb-1">Political Bias</label>
                <select
                  value={politicalBias}
                  onChange={(e) => setPoliticalBias(e.target.value)}
                  className="w-full rounded-lg border border-[#2a2a4a] bg-[#0a0a0f] px-3 py-2 text-sm text-[#e4e4ef] outline-none focus:border-[#4f8aff]/50"
                >
                  {POLITICAL_BIASES.map((b) => (
                    <option key={b} value={b}>{b}</option>
                  ))}
                </select>
              </div>
              <div>
                <label className="block text-xs text-[#9393b0] mb-1">Writing Style</label>
                <select
                  value={writingStyle}
                  onChange={(e) => setWritingStyle(e.target.value)}
                  className="w-full rounded-lg border border-[#2a2a4a] bg-[#0a0a0f] px-3 py-2 text-sm text-[#e4e4ef] outline-none focus:border-[#4f8aff]/50"
                >
                  {WRITING_STYLES.map((s) => (
                    <option key={s} value={s}>{s}</option>
                  ))}
                </select>
              </div>
              <div>
                <label className="block text-xs text-[#9393b0] mb-1">Interests (comma-separated)</label>
                <input
                  value={interests}
                  onChange={(e) => setInterests(e.target.value)}
                  placeholder="AI, cricket, politics"
                  className="w-full rounded-lg border border-[#2a2a4a] bg-[#0a0a0f] px-3 py-2 text-sm text-[#e4e4ef] placeholder-[#9393b0]/40 outline-none focus:border-[#4f8aff]/50"
                />
              </div>
            </div>

            <div className="mt-4 space-y-3">
              <SliderField label="Stubbornness" value={stubbornness} onChange={setStubbornness} low="Open-minded" high="Very stubborn" />
              <SliderField label="Curiosity" value={curiosity} onChange={setCuriosity} low="Indifferent" high="Very curious" />
              <SliderField label="Aggressiveness" value={aggressiveness} onChange={setAggressiveness} low="Peaceful" high="Aggressive" />
              <SliderField label="Humor" value={humor} onChange={setHumor} low="Serious" high="Very funny" />
            </div>
          </section>

          {/* Beliefs */}
          <section>
            <h3 className="text-sm font-semibold text-[#e4e4ef] mb-3">Core Beliefs &amp; Opinions</h3>
            <textarea
              value={beliefs}
              onChange={(e) => setBeliefs(e.target.value)}
              placeholder={"One per line, format — topic: stance\ne.g.\nAI: AI will augment not replace humans\nCricket: Virat Kohli is the GOAT\nClimate: Renewable energy is the future"}
              rows={4}
              className="w-full rounded-lg border border-[#2a2a4a] bg-[#0a0a0f] px-3 py-2 text-sm text-[#e4e4ef] placeholder-[#9393b0]/40 outline-none focus:border-[#4f8aff]/50 resize-none font-mono"
            />
          </section>

          {/* Group */}
          <section>
            <h3 className="text-sm font-semibold text-[#e4e4ef] mb-3">Assign to Group *</h3>
            <div className="grid grid-cols-2 gap-2">
              {groups.map((g) => (
                <button
                  key={g.slug}
                  onClick={() => setGroupSlug(g.slug)}
                  className={`rounded-lg border px-3 py-2 text-left text-sm transition-all ${
                    groupSlug === g.slug
                      ? "border-[#4f8aff] bg-[#4f8aff]/10 text-[#e4e4ef]"
                      : "border-[#2a2a4a] bg-[#0a0a0f] text-[#9393b0] hover:border-[#4f8aff]/30"
                  }`}
                >
                  <span className="font-medium">{g.name}</span>
                  <span className="block text-[10px] mt-0.5 opacity-60">{g.theme} · {g.agent_count} agents</span>
                </button>
              ))}
            </div>
          </section>
        </div>

        {error && (
          <div className="mx-6 mb-3 rounded-lg bg-red-500/10 border border-red-500/30 px-4 py-2">
            <p className="text-sm text-red-400">{error}</p>
          </div>
        )}

        <div className="sticky bottom-0 flex items-center justify-end gap-3 border-t border-[#2a2a4a] bg-[#12121a] px-6 py-4">
          <button
            onClick={onClose}
            className="rounded-lg border border-[#2a2a4a] px-4 py-2 text-sm text-[#9393b0] hover:text-[#e4e4ef] transition-colors"
          >
            Cancel
          </button>
          <button
            onClick={handleSubmit}
            disabled={submitting}
            className="rounded-lg bg-gradient-to-r from-[#4f8aff] to-[#8b5cf6] px-5 py-2 text-sm font-medium text-white transition-all hover:opacity-90 disabled:opacity-40"
          >
            {submitting ? "Creating..." : "Create Agent"}
          </button>
        </div>
      </div>
    </div>
  );
}


function SliderField({
  label,
  value,
  onChange,
  low,
  high,
}: {
  label: string;
  value: number;
  onChange: (v: number) => void;
  low: string;
  high: string;
}) {
  return (
    <div>
      <div className="flex items-center justify-between mb-1">
        <label className="text-xs text-[#9393b0]">{label}</label>
        <span className="text-xs text-[#4f8aff] font-mono">{value.toFixed(1)}</span>
      </div>
      <input
        type="range"
        min={0}
        max={1}
        step={0.1}
        value={value}
        onChange={(e) => onChange(Number(e.target.value))}
        className="w-full accent-[#4f8aff] h-1.5"
      />
      <div className="flex justify-between mt-0.5">
        <span className="text-[10px] text-[#9393b0]/60">{low}</span>
        <span className="text-[10px] text-[#9393b0]/60">{high}</span>
      </div>
    </div>
  );
}
