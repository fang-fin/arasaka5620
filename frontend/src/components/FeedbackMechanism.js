// import React, { useState, useEffect } from 'react';

// function FeedbackMechanism() {
//   const [feedback, setFeedback] = useState('');
//   const [feedbackHistory, setFeedbackHistory] = useState([]);

//   useEffect(() => {
//     fetchFeedbackHistory();
//   }, []);

//   // const fetchFeedbackHistory = async () => {
//   //   try {
//   //     const response = await fetch('/api/feedback');
//   //     const data = await response.json();
//   //     setFeedbackHistory(data.feedbacks);
//   //   } catch (error) {
//   //     console.error('Error fetching feedback history:', error);
//   //   }
//   // };
//   const fetchFeedbackHistory = async () => {
//     try {
//       const response = await fetch('/api/feedbacks');
//       const data = await response.json();

//       if (Array.isArray(data.feedbacks)) {
//         setFeedbackHistory(data.feedbacks);
//       } else {
//         console.error('Feedbacks is not an array', data);
//         setFeedbackHistory([]);  
//       }
//     } catch (error) {
//       console.error('Error fetching feedbacks:', error);
//       setFeedbackHistory([]);  
//     }
//   };
  

//   const handleSubmit = async (e) => {
//     e.preventDefault();
//     const userId = localStorage.getItem('userId'); // 获取用户ID
//     try {
//       const response = await fetch('/api/feedback', {
//         method: 'POST',
//         headers: {
//           'Content-Type': 'application/json',
//         },
//         body: JSON.stringify({
//           content: feedback,
//           timestamp: new Date().toISOString(),
//           userId: userId 
//         }),
//       });
//       if (response.ok) {
//         alert('Feedback submitted successfully');
//         setFeedback('');
//         fetchFeedbackHistory();
//       } else {
//         alert('Failed to submit feedback');
//       }
//     } catch (error) {
//       console.error('Error submitting feedback:', error);
//     }
//   };

//   return (
//     <div className="bg-white shadow-md rounded-lg p-6">
//       <h2 className="text-2xl font-bold mb-4">Feedback Mechanism</h2>
      
//       {/* Feedback Input */}
//       <div className="mb-6">
//         <form onSubmit={handleSubmit} className="space-y-4">
//           <div>
//             <label className="block text-sm font-medium text-gray-700 mb-1">
//               Your Feedback
//             </label>
//             <textarea
//               value={feedback}
//               onChange={(e) => setFeedback(e.target.value)}
//               className="w-full p-2 border rounded"
//               rows="4"
//               required
//             />
//           </div>
//           <button type="submit" className="w-full p-2 bg-blue-500 text-white rounded">
//             Submit Feedback
//           </button>
//         </form>
//       </div>

//       {/* Feedback History */}
//       <div>
//         <h3 className="text-xl font-semibold mb-2">Feedback History</h3>
//         <ul className="space-y-2">
//           {feedbackHistory.map((item, index) => (
//             <li key={index} className="border-b pb-2">
//               <p className="text-gray-600 text-sm">{new Date(item.timestamp).toLocaleString()}</p>
//               <p>{item.content}</p>
//             </li>
//           ))}
//         </ul>
//       </div>
//     </div>
//   );
// }

// export default FeedbackMechanism;

import React, { useState, useEffect } from 'react';

function FeedbackMechanism() {
  const [feedback, setFeedback] = useState('');
  const [feedbackHistory, setFeedbackHistory] = useState([]);

  useEffect(() => {
    fetchFeedbackHistory();
  }, []);

  // fetch feedback history
  const fetchFeedbackHistory = async () => {
    try {
      console.log('Fetching feedback history...');
      const response = await fetch('/api/feedback');
      console.log('Feedback response:', response);
      
      const data = await response.json();
      console.log('Feedback data:', data);
      
      if (data.success && Array.isArray(data.feedbackHistory)) {
        console.log('Setting feedback history:', data.feedbackHistory);
        setFeedbackHistory(data.feedbackHistory);
      } else {
        console.warn('Unexpected feedback data format:', data);
        setFeedbackHistory([]);
      }
    } catch (error) {
      console.error('Error fetching feedback:', error);
      setFeedbackHistory([]);
    }
  };
  

  // submit feedback
  const handleSubmit = async (e) => {
    e.preventDefault();

    const userId = localStorage.getItem('userId');
    
      // add debug information before request
    console.log('Submitting feedback:', {
      content: feedback,
      userId: userId,
      timestamp: new Date().toISOString()
    });


    try {
      const response = await fetch('/api/feedback', { // use correct path
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          content: feedback,
          timestamp: new Date().toISOString(),
          userId: userId  // pass user_id
        }),
      });
      
      // add debug information after response
      console.log('Feedback submission response:', {
        status: response.status,
        ok: response.ok
      });

      if (response.ok) {
        alert('Feedback submitted successfully');
        setFeedback(''); // clear feedback input
        fetchFeedbackHistory(); // re-fetch feedback history
      } else {
        alert('Failed to submit feedback');
      }
    } catch (error) {
      console.error('Error submitting feedback:', error);
    }
  };

  return (
    <div className="bg-white shadow-md rounded-lg p-6">
      <h2 className="text-2xl font-bold mb-4">Feedback Mechanism</h2>
      
      {/* submit feedback */}
      <div className="mb-6">
        <form onSubmit={handleSubmit} className="space-y-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Your Feedback
            </label>
            <textarea
              value={feedback}
              onChange={(e) => setFeedback(e.target.value)}
              className="w-full p-2 border rounded"
              rows="4"
              required
            />
          </div>
          <button type="submit" className="w-full p-2 bg-blue-500 text-white rounded">
            Submit Feedback
          </button>
        </form>
      </div>

      {/* feedback history */}
      <div>
        <h3 className="text-xl font-semibold mb-2">Feedback History</h3>
        <ul className="space-y-2">
          {feedbackHistory.map((item, index) => (
            <li key={index} className="border-b pb-2">
              <p className="text-gray-600 text-sm">{new Date(item.timestamp).toLocaleString()}</p>
              <p>{item.content}</p>
            </li>
          ))}
        </ul>
      </div>
    </div>
  );
}

export default FeedbackMechanism;
