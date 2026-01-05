#ifndef HTTP_REQUEST_MANAGER_H
#define HTTP_REQUEST_MANAGER_H

#include "IHttpRequestManager.h"
#include "IHttpRequestQueue.h"
#include "IHttpRequestProcessor.h"
#include <ServerFactory.h>
#include <iostream>

/// @Component
class HttpRequestManager final : public IHttpRequestManager {

    /// @Autowired
    Private IHttpRequestQueuePtr requestQueue;

    /// @Autowired
    Private IHttpRequestProcessorPtr requestProcessor;

    Private IServerPtr server;

    Public HttpRequestManager() 
        : server(ServerFactory::GetDefaultServer()) {
            server->Start(8080);
    }
    
    Public ~HttpRequestManager() override = default;

    // ============================================================================
    // HTTP Request Management Operations
    // ============================================================================
    
    Public Bool RetrieveRequest() override {
        if (server == nullptr) {
            return false;
        }
        
        IHttpRequestPtr request = server->ReceiveMessage();
        StdString requestId = request->GetRequestId();
        std::cout << "Request ID: " << requestId.c_str() << std::endl;
        if (request == nullptr) {
            return false;
        }
        
        requestQueue->EnqueueRequest(request);
        return true;
    }
    
    Public Bool ProcessRequest() override {
        if (requestProcessor == nullptr) {
            return false;
        }
        
        Bool processedAny = false;
        while (requestQueue->HasRequests()) {
            if (requestProcessor->ProcessRequest()) {
                processedAny = true;
            } else {
                break;
            }
        }
        
        return processedAny;
    }
};

#endif // HTTP_REQUEST_MANAGER_H

