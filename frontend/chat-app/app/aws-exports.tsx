// https://docs.amplify.aws/nextjs/build-a-backend/auth/set-up-auth/
import { Amplify } from 'aws-amplify';

Amplify.configure({
  Auth: {
    Cognito: {
      //  Amazon Cognito User Pool ID
      userPoolId: process.env.NEXT_PUBLIC_AMPLIFY_USERPOOL_ID || '',
      // OPTIONAL - Amazon Cognito Web Client ID (26-char alphanumeric string)
      userPoolClientId: process.env.NEXT_PUBLIC_COGNITO_USERPOOL_CLIENT_ID || '',
      // REQUIRED only for Federated Authentication - Amazon Cognito Identity Pool ID
      // identityPoolId: 'XX-XXXX-X:XXXXXXXX-XXXX-1234-abcd-1234567890ab',
      // OPTIONAL - This is used when autoSignIn is enabled for Auth.signUp
      // 'code' is used for Auth.confirmSignUp, 'link' is used for email link verification
      signUpVerificationMethod: 'code', // 'code' | 'link'
    }
  }
});

// You can get the current config object
const currentConfig = Amplify.getConfig();

export default currentConfig;