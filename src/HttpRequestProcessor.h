#ifndef HTTP_REQUEST_PROCESSOR_H
#define HTTP_REQUEST_PROCESSOR_H

#include "IHttpRequestProcessor.h"
#include "IHttpRequestQueue.h"
#include "IHttpRequestDispatcher.h"
#include "IHttpResponseQueue.h"
#include <IHttpResponse.h>
#include <iostream>

/// @Component
class HttpRequestProcessor final : public IHttpRequestProcessor {

    /// @Autowired
    Private IHttpRequestQueuePtr requestQueue;

    /// @Autowired
    Private IHttpRequestDispatcherPtr dispatcher;

    /// @Autowired
    Private IHttpResponseQueuePtr responseQueue;

    Public HttpRequestProcessor() = default;
    
    Public ~HttpRequestProcessor() override = default;

    // ============================================================================
    // HTTP Request Processing Operations
    // ============================================================================
    
    Public Bool ProcessRequest() override {
        std::cout << "[HttpRequestProcessor] ProcessRequest() called" << std::endl;
        
        if (requestQueue->IsEmpty()) {
            std::cout << "[HttpRequestProcessor] Request queue is empty" << std::endl;
            return false;
        }
        
        std::cout << "[HttpRequestProcessor] Request queue is not empty, dequeuing..." << std::endl;
        IHttpRequestPtr request = requestQueue->DequeueRequest();
        if (request == nullptr) {
            std::cout << "[HttpRequestProcessor] ERROR: Dequeued request is nullptr" << std::endl;
            return false;
        }
        
        std::cout << "[HttpRequestProcessor] Successfully dequeued request" << std::endl;
        
        // Dispatch request to get response body
        std::cout << "[HttpRequestProcessor] Calling DispatchRequest()..." << std::endl;
        StdString responseBody = dispatcher->DispatchRequest(request);
        std::cout << "[HttpRequestProcessor] DispatchRequest() returned body length: " << responseBody.length() << std::endl;
        if (responseBody.length() > 0) {
            std::cout << "[HttpRequestProcessor] Response body preview (first 100 chars): " << responseBody.substr(0, 100) << std::endl;
        }
        
        // Get request ID from the request
        StdString requestId = StdString(request->GetRequestId());
        std::cout << "[HttpRequestProcessor] Request ID: '" << requestId << "' (length: " << requestId.length() << ")" << std::endl;
        if (requestId.empty()) {
            std::cout << "[HttpRequestProcessor] ERROR: Request ID is empty!" << std::endl;
            return false;
        }
        
        // Create HTTP response with request ID and response body
        std::cout << "[HttpRequestProcessor] Creating response with requestId='" << requestId << "', body length=" << responseBody.length() << std::endl;
        IHttpResponsePtr response = IHttpResponse::GetResponse(requestId, responseBody);
        if (response == nullptr) {
            std::cout << "[HttpRequestProcessor] ERROR: IHttpResponse::GetResponse() returned nullptr!" << std::endl;
            std::cout << "[HttpRequestProcessor] requestId.empty()=" << (requestId.empty() ? "true" : "false") << std::endl;
            std::cout << "[HttpRequestProcessor] responseBody.empty()=" << (responseBody.empty() ? "true" : "false") << std::endl;
            return false;
        }
        
        std::cout << "[HttpRequestProcessor] Successfully created response" << std::endl;
        
        // Enqueue response into response queue
        std::cout << "[HttpRequestProcessor] Enqueueing response..." << std::endl;
        responseQueue->EnqueueResponse(response);
        std::cout << "[HttpRequestProcessor] Response enqueued successfully" << std::endl;
        
        return true;
    }
};

#endif // HTTP_REQUEST_PROCESSOR_H

