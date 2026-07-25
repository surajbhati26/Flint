# Vercel Speed Insights Setup for EducatorAssessmentPro

## Overview
Vercel Speed Insights has been integrated into this Streamlit application to track and monitor real-time web performance metrics.

## What Was Implemented

The Speed Insights integration was added to `flint/app.py` using the vanilla JavaScript approach, which is compatible with Streamlit's component system.

### Changes Made:
1. **Added imports**: `streamlit.components.v1` and `os` modules
2. **Created `inject_speed_insights()` function**: This function injects the Speed Insights JavaScript tracking code into the Streamlit app
3. **Automatic initialization**: The function is called automatically when the app starts

## How It Works

The integration works by:
1. Checking for the `VERCEL_ANALYTICS_ID` environment variable (automatically set by Vercel when deployed)
2. If present, injecting the Speed Insights JavaScript snippet using Streamlit's `components.html()` function
3. The script runs in the background and collects performance metrics without interfering with the app's functionality

## Deployment Requirements

For Speed Insights to work, you need to:

### 1. Deploy to Vercel
This app must be deployed on Vercel for Speed Insights to function. The tracking code only activates when the `VERCEL_ANALYTICS_ID` environment variable is present.

### 2. Enable Speed Insights in Vercel Dashboard
1. Go to your project in the Vercel dashboard
2. Navigate to the "Speed Insights" tab
3. Click "Enable Speed Insights"
4. Redeploy your application

### 3. Verify Installation
After deployment and enabling Speed Insights:
1. Visit your deployed application
2. Navigate through different tabs/pages
3. Return to Vercel dashboard → Speed Insights
4. You should see performance metrics appearing (may take a few minutes for first data to show)

## Performance Metrics Tracked

Speed Insights automatically tracks:
- **TTFB** (Time to First Byte): Server response time
- **FCP** (First Contentful Paint): Time until first content is visible
- **LCP** (Largest Contentful Paint): Time until main content is loaded
- **FID** (First Input Delay): Time until page becomes interactive
- **CLS** (Cumulative Layout Shift): Visual stability metric

## Local Development

When running locally (`streamlit run app.py`), the Speed Insights code will not execute because the `VERCEL_ANALYTICS_ID` environment variable is not set. This is intentional and allows for normal local development without tracking.

## Troubleshooting

### Speed Insights not showing data?
- Ensure Speed Insights is enabled in your Vercel project settings
- Verify the app is deployed on Vercel (not just running locally)
- Wait 5-10 minutes after first deployment for data to appear
- Check that you've had actual user visits to the deployed site

### Streamlit component errors?
- Ensure you have `streamlit>=1.38.0` installed
- The `components.html()` function is part of Streamlit's core functionality

## Technical Details

The implementation uses the vanilla JavaScript approach recommended by Vercel for non-framework applications:

```javascript
window.si = window.si || function () { 
    (window.siq = window.siq || []).push(arguments); 
};
```

This creates a lightweight queue for tracking events before the main Speed Insights script loads asynchronously from `/_vercel/speed-insights/script.js`.

## Benefits

With Speed Insights enabled, you can:
- Monitor real-world performance across different users and devices
- Identify performance bottlenecks in your Streamlit app
- Track Core Web Vitals for SEO and user experience optimization
- Get insights on page load times and interaction delays
- Make data-driven decisions to improve app performance

## Additional Resources

- [Vercel Speed Insights Documentation](https://vercel.com/docs/speed-insights)
- [Vercel Speed Insights Quickstart](https://vercel.com/docs/speed-insights/quickstart)
- [Streamlit Components Documentation](https://docs.streamlit.io/library/components)
