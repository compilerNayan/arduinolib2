#ifndef HTTP_REQUEST_DISPATCHER_H
#define HTTP_REQUEST_DISPATCHER_H

#include <unordered_map>
#include <NayanSerializer.h>
#include "EndpointTrie.h"
#include <StandardDefines.h>
#include <sstream>
#include <stdexcept>
#include <type_traits>
#include <algorithm>
#include <cctype>

#include "IHttpRequestDispatcher.h"

/// @Component
class HttpRequestDispatcher : public IHttpRequestDispatcher {

    Private UnorderedMap<StdString, std::function<StdString(CStdString, Map<StdString, StdString>)>> getMappings;
    Private UnorderedMap<StdString, std::function<StdString(CStdString, Map<StdString, StdString>)>> postMappings;
    Private UnorderedMap<StdString, std::function<StdString(CStdString, Map<StdString, StdString>)>> putMappings;
    Private UnorderedMap<StdString, std::function<StdString(CStdString, Map<StdString, StdString>)>> patchMappings;
    Private UnorderedMap<StdString, std::function<StdString(CStdString, Map<StdString, StdString>)>> deleteMappings;
    Private UnorderedMap<StdString, std::function<StdString(CStdString, Map<StdString, StdString>)>> optionsMappings;
    Private UnorderedMap<StdString, std::function<StdString(CStdString, Map<StdString, StdString>)>> headMappings;
    Private UnorderedMap<StdString, std::function<StdString(CStdString, Map<StdString, StdString>)>> traceMappings;
    Private UnorderedMap<StdString, std::function<StdString(CStdString, Map<StdString, StdString>)>> connectMappings;

    Private EndpointTrie endpointTrie;

    Public HttpRequestDispatcher() {
        InitializeMappings();
    }

    Public ~HttpRequestDispatcher() = default;

    Public StdString DispatchRequest(IHttpRequestPtr request) override {
        CStdString url = request->GetPath();
        CStdString payload = request->GetBody();
        EndpointMatchResult result = endpointTrie.Search(url);
        if(result.found == false) {
            return StdString();
        }
        Val variables = result.variables;
        Val patternUrl = result.pattern;

        try {
            switch (request->GetMethod()) {
                case HttpMethod::GET:
                    return getMappings[patternUrl](payload, variables);
                case HttpMethod::POST:
                    return postMappings[patternUrl](payload, variables);
                case HttpMethod::PUT:
                    return putMappings[patternUrl](payload, variables);
                case HttpMethod::PATCH:
                    return patchMappings[patternUrl](payload, variables);
                case HttpMethod::DELETE:
                    return deleteMappings[patternUrl](payload, variables);
                case HttpMethod::OPTIONS:
                    return optionsMappings[patternUrl](payload, variables);
                case HttpMethod::HEAD:
                    return headMappings[patternUrl](payload, variables);
                case HttpMethod::TRACE:
                    return traceMappings[patternUrl](payload, variables);
                case HttpMethod::CONNECT:
                    return connectMappings[patternUrl](payload, variables);
            } 
            return StdString();
    
        } catch (const std::exception& e) {
            return StdString("{\"error\":\"Internal Server Error\"}");
        }

    }

    Private Void InitializeMappings() {

    }

    /**
     * Template function to convert a string to a given type.
     * 
     * - If Type is string-related (StdString, CStdString, std::string, string), returns as-is
     * - If Type is a primitive type (int, Int, long, Long, float, double, bool, etc.), converts from string
     * - Handles types from StandardDefines.h (Int, Long, UInt, ULong, Bool, etc.)
     * 
     * @tparam Type The target type to convert to
     * @param str The input string to convert
     * @return The converted value of type Type
     */
    Public template<typename Type>
    Static Type ConvertToType(CStdString str) {
        // Handle string types - return as-is
        if constexpr (std::is_same_v<Type, StdString> || 
                      std::is_same_v<Type, CStdString> ||
                      std::is_same_v<Type, std::string> ||
                      std::is_same_v<Type, const std::string>) {
            return StdString(str);
        }
        // Handle boolean types (bool, Bool, CBool)
        else if constexpr (std::is_same_v<Type, bool> || 
                          std::is_same_v<Type, Bool> || 
                          std::is_same_v<Type, CBool>) {
            StdString lower = str;
            std::transform(lower.begin(), lower.end(), lower.begin(), ::tolower);
            if (lower == "true" || lower == "1") {
                return true;
            } else if (lower == "false" || lower == "0") {
                return false;
            } else {
                throw std::invalid_argument("Invalid boolean value: " + StdString(str));
            }
        }
        // Handle signed integer types (int, Int, CInt, long, Long, CLong, etc.)
        else if constexpr (std::is_integral_v<Type> && std::is_signed_v<Type>) {
            try {
                if constexpr (sizeof(Type) <= sizeof(int)) {
                    return static_cast<Type>(std::stoi(str));
                } else if constexpr (sizeof(Type) <= sizeof(long)) {
                    return static_cast<Type>(std::stol(str));
                } else {
                    return static_cast<Type>(std::stoll(str));
                }
            } catch (const std::exception& e) {
                throw std::invalid_argument("Invalid signed integer value: " + StdString(str));
            }
        }
        // Handle unsigned integer types (unsigned int, UInt, CUInt, unsigned long, ULong, CULong, etc.)
        else if constexpr (std::is_integral_v<Type> && std::is_unsigned_v<Type>) {
            try {
                if constexpr (sizeof(Type) <= sizeof(unsigned int)) {
                    return static_cast<Type>(std::stoul(str));
                } else if constexpr (sizeof(Type) <= sizeof(unsigned long)) {
                    return static_cast<Type>(std::stoul(str));
                } else {
                    return static_cast<Type>(std::stoull(str));
                }
            } catch (const std::exception& e) {
                throw std::invalid_argument("Invalid unsigned integer value: " + StdString(str));
            }
        }
        // Handle floating point types (float, double, long double)
        else if constexpr (std::is_floating_point_v<Type>) {
            try {
                if constexpr (std::is_same_v<Type, float>) {
                    return std::stof(str);
                } else if constexpr (std::is_same_v<Type, double>) {
                    return std::stod(str);
                } else {
                    return std::stold(str);
                }
            } catch (const std::exception& e) {
                throw std::invalid_argument("Invalid floating point value: " + StdString(str));
            }
        }
        // Handle character types (char, Char, CChar, unsigned char, UChar, CUChar, UInt8)
        else if constexpr (std::is_same_v<Type, char> || 
                          std::is_same_v<Type, Char> || 
                          std::is_same_v<Type, CChar> ||
                          std::is_same_v<Type, unsigned char> || 
                          std::is_same_v<Type, UChar> || 
                          std::is_same_v<Type, CUChar> ||
                          std::is_same_v<Type, UInt8>) {
            if (str.length() == 1) {
                return static_cast<Type>(str[0]);
            } else if (str.length() == 0) {
                return static_cast<Type>(0);
            } else {
                // Try to parse as integer for character types
                try {
                    return static_cast<Type>(std::stoi(str));
                } catch (const std::exception& e) {
                    throw std::invalid_argument("Invalid character value: " + StdString(str));
                }
            }
        }
        // Fallback: for non-primitive, non-string types, use SerializationUtility::Deserialize
        else {
            return nayan::serializer::SerializationUtility::Deserialize<Type>(str);
        }
    }

};

#endif // HTTP_REQUEST_DISPATCHER_H