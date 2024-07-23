import React, { useState } from 'react';
import { Auth } from 'aws-amplify';

const SignIn = () => {
  const [identifier, setIdentifier] = useState('');
  const [code, setCode] = useState('');
  const [step, setStep] = useState(1);
  const [user, setUser] = useState(null);

  const handleSendCode = async () => {
    try {
      const cognitoUser = await Auth.signIn(identifier);
      setUser(cognitoUser);
      if (cognitoUser.challengeName === 'CUSTOM_CHALLENGE') {
        setStep(2);
      } else {
        console.log('Unexpected challenge:', cognitoUser);
      }
    } catch (error) {
      if (error.code === 'UserNotFoundException') {
        try {
          await Auth.signUp({
            username: identifier,
            password: Math.random().toString(36).slice(-8), // Temporary password
            attributes: {
              email: identifier.includes('@') ? identifier : undefined,
              phone_number: identifier.match(/^\+?[1-9]\d{1,14}$/) ? identifier : undefined,
            },
          });
          const cognitoUser = await Auth.signIn(identifier);
          setUser(cognitoUser);
          if (cognitoUser.challengeName === 'CUSTOM_CHALLENGE') {
            setStep(2);
          }
        } catch (signUpError) {
          console.error('Error during sign-up:', signUpError);
        }
      } else {
        console.error('Error during sign-in:', error);
      }
    }
  };

  const handleConfirmSignIn = async () => {
    try {
      const cognitoUser = await Auth.sendCustomChallengeAnswer(user, code);
      if (cognitoUser.challengeName === 'CUSTOM_CHALLENGE') {
        setStep(2);
      } else {
        console.log('User signed in successfully:', cognitoUser);
        // You might want to redirect the user to another page or update the UI
      }
    } catch (error) {
      console.error('Error confirming sign in:', error);
    }
  };

  return (
      <div>
        {step === 1 && (
            <div>
              <input
                  type="text"
                  placeholder="Email or Phone Number"
                  value={identifier}
                  onChange={(e) => setIdentifier(e.target.value)}
              />
              <button onClick={handleSendCode}>Send Code</button>
            </div>
        )}
        {step === 2 && (
            <div>
              <input
                  type="text"
                  placeholder="Verification Code"
                  value={code}
                  onChange={(e) => setCode(e.target.value)}
              />
              <button onClick={handleConfirmSignIn}>Confirm Sign In</button>
            </div>
        )}
      </div>
  );
};

export default SignIn;
