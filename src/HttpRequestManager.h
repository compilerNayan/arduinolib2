#ifndef HTTP_REQUEST_MANAGER_H
#define HTTP_REQUEST_MANAGER_H

#include "IHttpRequestManager.h"
#include "IHttpRequestQueue.h"
#include "IHttpRequestProcessor.h"
#include "IHttpResponseProcessor.h"
#include <ServerProvider.h>

/* @Component */
class HttpRequestManager final : public IHttpRequestManager {

    /* @Autowired */
    Private IHttpRequestQueuePtr requestQueue;

    /* @Autowired */
    Private IHttpRequestProcessorPtr requestProcessor;

    /* @Autowired */
    Private IHttpResponseProcessorPtr responseProcessor;

    Private IServerPtr server;

    Public HttpRequestManager() {
#ifdef ARDUINO
        Serial.println("[HttpRequestManager] Constructor called");
        Serial.print("[HttpRequestManager] Checking registered server count: ");
        Serial.println(ServerProvider::GetRegisteredCount());
#else
        std::cout << "[HttpRequestManager] Constructor called" << std::endl;
        std::cout << "[HttpRequestManager] Checking registered server count: " << ServerProvider::GetRegisteredCount() << std::endl;
#endif
        
        server = ServerProvider::GetDefaultServer();
        
#ifdef ARDUINO
        if (server == nullptr) {
            Serial.println("[HttpRequestManager] ERROR: GetDefaultServer() returned nullptr!");
            Serial.println("[HttpRequestManager] This means no servers were registered.");
            Serial.println("[HttpRequestManager] Check ServerProviderInit.h - it should register servers.");
        } else {
            Serial.println("[HttpRequestManager] GetDefaultServer() returned valid server instance");
        }
#else
        if (server == nullptr) {
            std::cout << "[HttpRequestManager] ERROR: GetDefaultServer() returned nullptr!" << std::endl;
            std::cout << "[HttpRequestManager] This means no servers were registered." << std::endl;
            std::cout << "[HttpRequestManager] Check ServerProviderInit.h - it should register servers." << std::endl;
        } else {
            std::cout << "[HttpRequestManager] GetDefaultServer() returned valid server instance" << std::endl;
        }
#endif
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
    
    Public Bool ProcessResponse() override {
        if (responseProcessor == nullptr) {
            return false;
        }
        
        Bool processedAny = false;
        // Process responses until queue is empty or processor returns false
        while (true) {
            if (responseProcessor->ProcessResponse()) {
                processedAny = true;
            } else {
                break;
            }
        }
        
        return processedAny;
    }
    
    Public Bool StartServer(CUInt port = DEFAULT_SERVER_PORT) override {
#ifdef ARDUINO
        Serial.print("[HttpRequestManager] StartServer() called with port: ");
        Serial.println(port);
#else
        std::cout << "[HttpRequestManager] StartServer() called with port: " << port << std::endl;
#endif
        
        if (server == nullptr) {
#ifdef ARDUINO
            Serial.println("[HttpRequestManager] ERROR: server is nullptr! Cannot start server.");
#else
            std::cout << "[HttpRequestManager] ERROR: server is nullptr! Cannot start server." << std::endl;
#endif
            return false;
        }
        
#ifdef ARDUINO
        Serial.println("[HttpRequestManager] Calling server->Start()...");
#else
        std::cout << "[HttpRequestManager] Calling server->Start()..." << std::endl;
#endif
        
        Bool result = server->Start(port);
        
        if (result) {
#ifdef ARDUINO
            Serial.println("[HttpRequestManager] server->Start() returned true - server started successfully");
#else
            std::cout << "[HttpRequestManager] server->Start() returned true - server started successfully" << std::endl;
#endif
        } else {
#ifdef ARDUINO
            Serial.println("[HttpRequestManager] ERROR: server->Start() returned false - server failed to start");
#else
            std::cout << "[HttpRequestManager] ERROR: server->Start() returned false - server failed to start" << std::endl;
#endif
        }
        
        return result;
    }
    
    Public Void StopServer() override {
        if (server != nullptr) {
            server->Stop();
        }
    }
};

#endif // HTTP_REQUEST_MANAGER_H

