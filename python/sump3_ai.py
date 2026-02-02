########################################################################
# This file is part of the SUMP3 project.
#
# Copyright (C) 2026  Kevin M. Hubbard BlackMesaLabs
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.
########################################################################
class SUMP3_AI:
  def ask_ai(self, prompt, ai_engine="gemini", api_key=None):
    ai_engine = ai_engine.lower();
    if ai_engine == "gemini":
      return self.ask_gemini(prompt, api_key);
    else:
      return f"Unknown ai_engine: {ai_engine}";

  def is_ai_request(self, prompt):
    import string;
    AI_TRIGGERS = { "how", "why", "what", "when", "where", "which", "who", "explain",
                    "describe", "tell", "show", "help", "analyze", "interpret",
                    "summarize", "compare", "count", "find", "identify", "measure",
                    "detect", "decode", "please", "can", "could", "would" };
    tokens = [t.strip(string.punctuation) for t in prompt.lower().split()];
    return any(t in AI_TRIGGERS for t in tokens);

  def create_sample_data(self):
    data = {
      "signal" : "sigA",
      "time_units" : "seconds",
      "value_units" : "mV",
      "edges" : [
        {"time": 0.000100, "value": 0.0 },
        {"time": 0.000120, "value": 0.1 },
        {"time": 0.000150, "value": 2.0 },
        {"time": 0.000200, "value": 3.1 },
        {"time": 0.000250, "value": -4.0 },
        {"time": 0.000300, "value": 1.0 },
        {"time": 0.000400, "value": 2.0 },
      ],
      "cursor_left": 0.000120,
      "cursor_right": 0.000250
     };
    return data;

  def ask_gemini(self, prompt, api_key=None):
    from google import genai

    # If api_key is None, the client auto‑reads GEMINI_API_KEY
    client = genai.Client() if api_key is None else genai.Client(api_key=api_key);
    try:
      response = client.models.generate_content( model="gemini-2.5-flash", contents=prompt);
      return response.text.strip();
    except Exception as e:
      return f"AI error: {type(e).__name__}: {e}";

def _self_test():
    ai = SUMP3_AI()
    api_key = None;
#   prompt  = "Provide only a numeric answer: what is 2+3?";

    data = ai.create_sample_data();
    prompt  = "In plain text format: At what time in us does sigA reach 3.1mV?\n %s" % str(data);

    if ai.is_ai_request( prompt ):
      rts = ai.ask_ai(prompt, ai_engine="gemini", api_key=api_key);
      print(rts);
#     assert int(rts.strip().split()[0]) == 5;
    else:
      Pass;
      # Do something else

if __name__ == "__main__":
  _self_test();
