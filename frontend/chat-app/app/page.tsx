'use client';

import React from 'react';
import { Amplify } from 'aws-amplify';
import * as Auth from 'aws-amplify/auth';
import { Authenticator } from '@aws-amplify/ui-react';
import '@aws-amplify/ui-react/styles.css';
import ChatApp from './components/ChatApp';

import awsconfig from './aws-exports';
// import Home from './components/Home';


Amplify.configure(awsconfig, {ssr: true});

export default function IndexPage() {

  const handleSignOut = async () => {
    try {
      await Auth.signOut();
      // Additional code if needed after successful sign-out
    } catch (error) {
      console.error('Error signing out:', error);
    }
  };

  const formFields = {
    signUp: {
      username: {
        order: 1
      },
      email: {
        order:2
      },
      password: {
        order: 3
      },
      confirm_password: {
        order: 4
      }
    },
  }

  return (
    <Authenticator formFields={formFields} signUpAttributes={['email']}>
      {({ signOut, user }) => (
        <div className="bg-gray-100 min-h-screen flex flex-col justify-center items-center">
        <header className="bg-white p-4 shadow-sm w-full flex justify-between">
          <h1 className="text-2xl font-semibold text-gray-800">Chatty</h1>
          <div className="flex items-center">
          <div className="mr-4 text-gray-600 hover:text-gray-800">Welcome {user?.username}!</div>
          <button
            onClick={handleSignOut}
            className="px-4 text-gray-600 hover:text-gray-800 hover:shadow-sm rounded-lg focus:outline-none"
          >
            Sign out
          </button>
        </div>
        </header>
        <main className="flex-grow p-4 flex items-center justify-center w-1/2 h-80">
            <div className="w-full h-90">
              <ChatApp />
            </div>
        </main>
        <footer className="bg-white p-4 shadow-sm w-full text-xs">
          <p className="text-center text-gray-600">
            &copy; {new Date().getFullYear()} Your Company, all rights reserved.
          </p>
          <p className="text-center text-gray-600 text-xs">
            AI answers should be verified before use.
          </p>
        </footer>
      </div>
      )}
  </Authenticator>
  );
};
