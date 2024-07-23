// src/components/VerifyOTP.js
import React, { useState } from 'react';
import { Auth } from 'aws-amplify';

function VerifyOTP({ user }) {
    const [otp, setOtp] = useState('');

    const handleVerifyOTP = async () => {
        try {
            const result = await Auth.sendCustomChallengeAnswer(user, otp);
            console.log('OTP verification successful!', result);
        } catch (error) {
            console.error('Error verifying OTP:', error);
        }
    };

    return (
        <div>
            <h2>Verify OTP</h2>
            <input
                type="text"
                value={otp}
                onChange={(e) => setOtp(e.target.value)}
                placeholder="OTP Code"
            />
            <button onClick={handleVerifyOTP}>Verify OTP</button>
        </div>
    );
}

export default VerifyOTP;
