# FreeSpeech

### Our project created for NatHacks 2024: FreeSpeech  
**Giving individuals the ability to talk without talking!**

---

## Overview
FreeSpeech is an innovative app developed for NatHacks 2024 that harnesses EEG data from a Muse2 headset. It processes motor signals using advanced signal processing techniques to interpret actions such as "left," "right," or "blinking." These inputs control a **Tkinter-based GUI**, allowing users to select corresponding letters and craft messages.

---

## Requirements

1. **Petal Metrics Software**  
   Ensure that the Petal Metrics software is installed, as it streams EEG data from the Muse2 headset.

2. **Muselsl Library**  
   Install the `muselsl` library to stream and analyze EEG data from the Muse headset. You can install it using:
   ```bash
   pip install muselsl

